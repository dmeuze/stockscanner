import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import MACD
from datetime import datetime
from jinja2 import Template
import time
import random
import numpy as np
import requests
import json
import os

def get_exchange():
    """Initialize and return the exchange with error handling"""
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,  # Enable built-in rate limiter
            'timeout': 30000,  # Increase timeout to 30 seconds
        })
        return exchange
    except Exception as e:
        print(f"Fout bij initialiseren exchange: {e}")
        return None

def fetch_ohlcv_with_retry(exchange, symbol, timeframe="1d", limit=200, max_retries=3):
    """Fetch OHLCV data with retry mechanism"""
    for attempt in range(max_retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            if not ohlcv:
                print(f"Geen data ontvangen voor {symbol}")
                return None
            return pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        except Exception as e:
            if "Too Many Requests" in str(e):
                wait_time = random.uniform(2, 5)
                print(f"Rate limit bereikt voor {symbol}, wacht {wait_time:.1f} seconden...")
                time.sleep(wait_time)
                continue
            print(f"Fout bij ophalen data voor {symbol}: {e}")
            return None
    return None

def get_top_100_binance_symbols():
    """Geeft alleen de opgegeven lijst van symbolen terug."""
    return [
        "BTC/USDT", "DOGE/USDT", "PEPE/USDT", "SOL/USDT", "ONDO/USDT",
        "LINK/USDT", "DOT/USDT", "ETH/USDT", "XRP/USDT", "ALAB/USDT"
    ]

def run_screener(strategy=None, symbols=None, timeframe='1d'):
    """Main function to run the crypto screener. If strategy is given, only that strategy is run. Als symbols is opgegeven, scan alleen deze. Timeframe bepaalt de candle-grootte."""
    exchange = get_exchange()
    if not exchange:
        print("Kon geen verbinding maken met de exchange. Script wordt afgebroken.")
        return None

    if symbols is None:
        symbols = get_top_100_binance_symbols()

    strategieen_map = {
        "rsi": "RSI Oversold/Overbought",
        "bollinger": "Bollinger Bounce/Breakdown",
        "macd": "MACD Crossover",
        "ma": "Trendvolgend (MA)",
        "volume": "Volume Spike",
        "golden_cross": "Golden/Death Cross"
    }

    strategieen = {
        "RSI Oversold/Overbought": {
            "beschrijving": "Detecteert oververkochte (RSI < 30) en overgekochte (RSI > 70) situaties.", 
            "matches": [],
            "verkoop_matches": []
        },
        "Bollinger Bounce/Breakdown": {
            "beschrijving": "Koers onder onderste Bollinger Band (kans op reversal) of boven bovenste band (kans op breakdown).", 
            "matches": [],
            "verkoop_matches": []
        },
        "MACD Crossover": {
            "beschrijving": "MACD-lijn kruist boven signaallijn (koop) of onder signaallijn (verkoop).", 
            "matches": [],
            "verkoop_matches": []
        },
        "Trendvolgend (MA)": {
            "beschrijving": "MA50 boven MA200 en prijs boven MA50 (koop) of MA50 onder MA200 en prijs onder MA50 (verkoop).", 
            "matches": [],
            "verkoop_matches": []
        },
        "Volume Spike": {
            "beschrijving": "Volume is > 1.5x het 30-daags gemiddelde: mogelijk institutionele aankoop/verkoop.", 
            "matches": [],
            "verkoop_matches": []
        },
        "Golden/Death Cross": {
            "beschrijving": "MA50 kruist boven MA200 (Golden Cross) of onder MA200 (Death Cross).", 
            "matches": [],
            "verkoop_matches": []
        }
    }

    if strategy:
        strategieen = {strategieen_map[strategy]: strategieen[strategieen_map[strategy]]}

    print(f"Start crypto screener... (timeframe: {timeframe})")
    for symbol in symbols:
        print(f"\nAnalyseren van {symbol}...")
        try:
            df = fetch_ohlcv_with_retry(exchange, symbol, timeframe=timeframe)
            if df is None or df.empty:
                print(f"Geen data beschikbaar voor {symbol}")
                continue

            close = df["close"]
            volume = df["volume"]
            current_price = close.iloc[-1]

            if not strategy or strategy == "rsi":
                rsi = RSIIndicator(close).rsi().iloc[-1]
                if not pd.isna(rsi):
                    if rsi < 30:
                        strategieen["RSI Oversold/Overbought"]["matches"].append((symbol, current_price, round(rsi, 2)))
                    elif rsi > 70:
                        strategieen["RSI Oversold/Overbought"]["verkoop_matches"].append((symbol, current_price, round(rsi, 2)))

            if not strategy or strategy == "bollinger":
                bb = BollingerBands(close)
                lower_bb = bb.bollinger_lband().iloc[-1]
                upper_bb = bb.bollinger_hband().iloc[-1]
                if not pd.isna(lower_bb) and not pd.isna(upper_bb):
                    if close.iloc[-1] < lower_bb:
                        strategieen["Bollinger Bounce/Breakdown"]["matches"].append((symbol, current_price, None))
                    elif close.iloc[-1] > upper_bb:
                        strategieen["Bollinger Bounce/Breakdown"]["verkoop_matches"].append((symbol, current_price, None))

            if not strategy or strategy == "macd":
                macd = MACD(close)
                macd_line = macd.macd()
                signal_line = macd.macd_signal()
                if not pd.isna(macd_line.iloc[-1]) and not pd.isna(signal_line.iloc[-1]):
                    if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                        strategieen["MACD Crossover"]["matches"].append((symbol, current_price, None))
                    elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                        strategieen["MACD Crossover"]["verkoop_matches"].append((symbol, current_price, None))

            if not strategy or strategy == "ma":
                ma50 = close.rolling(window=50).mean()
                ma200 = close.rolling(window=200).mean()
                if not pd.isna(ma50.iloc[-1]) and not pd.isna(ma200.iloc[-1]):
                    if ma50.iloc[-1] > ma200.iloc[-1] and current_price > ma50.iloc[-1]:
                        strategieen["Trendvolgend (MA)"]["matches"].append((symbol, current_price, None))
                    elif ma50.iloc[-1] < ma200.iloc[-1] and current_price < ma50.iloc[-1]:
                        strategieen["Trendvolgend (MA)"]["verkoop_matches"].append((symbol, current_price, None))

            if not strategy or strategy == "volume":
                avg_vol = volume.rolling(window=30).mean().iloc[-2]
                if not pd.isna(avg_vol) and volume.iloc[-1] > avg_vol * 1.5:
                    if close.iloc[-1] > close.iloc[-2]:
                        strategieen["Volume Spike"]["matches"].append((symbol, current_price, round(volume.iloc[-1], 0)))
                    else:
                        strategieen["Volume Spike"]["verkoop_matches"].append((symbol, current_price, round(volume.iloc[-1], 0)))

            if not strategy or strategy == "golden_cross":
                ma50 = close.rolling(window=50).mean()
                ma200 = close.rolling(window=200).mean()
                if not pd.isna(ma50.iloc[-1]) and not pd.isna(ma200.iloc[-1]):
                    if ma50.iloc[-1] > ma200.iloc[-1] and ma50.iloc[-2] <= ma200.iloc[-2]:
                        strategieen["Golden/Death Cross"]["matches"].append((symbol, current_price, None))
                    elif ma50.iloc[-1] < ma200.iloc[-1] and ma50.iloc[-2] >= ma200.iloc[-2]:
                        strategieen["Golden/Death Cross"]["verkoop_matches"].append((symbol, current_price, None))

            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"Fout bij {symbol}: {e}")

    for s in strategieen.values():
        if len(s["matches"]) > 0:
            prijzen = [float(p[1]) for p in s["matches"]]
            s["best_price"] = float(min(prijzen))
        else:
            s["best_price"] = None
            
        if len(s["verkoop_matches"]) > 0:
            prijzen = [float(p[1]) for p in s["verkoop_matches"]]
            s["best_verkoop_price"] = float(max(prijzen))
        else:
            s["best_verkoop_price"] = None

    # Maak results directory als deze nog niet bestaat
    os.makedirs('results', exist_ok=True)
    
    # Sla resultaten op in JSON bestand
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/crypto_{strategy if strategy else 'all'}_{timestamp}.json"
    
    # Converteer tuples naar lijsten voor JSON serialisatie
    json_data = {}
    for naam, data in strategieen.items():
        json_data[naam] = {
            "beschrijving": data["beschrijving"],
            "matches": [[symbol, float(price), float(extra) if extra is not None else None] 
                       for symbol, price, extra in data["matches"]],
            "verkoop_matches": [[symbol, float(price), float(extra) if extra is not None else None] 
                               for symbol, price, extra in data["verkoop_matches"]],
            "best_price": float(data["best_price"]) if data["best_price"] is not None else None,
            "best_verkoop_price": float(data["best_verkoop_price"]) if data["best_verkoop_price"] is not None else None
        }
    
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4)
    
    print(f"Resultaten opgeslagen in {filename}")
    return strategieen 