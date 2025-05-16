from crypto_base import get_exchange, get_top_100_binance_symbols, fetch_ohlcv_with_retry, generate_html_dashboard
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time
import random

def analyze_sell_signals(df, current_price):
    """Analyze potential sell signals for a given dataframe"""
    sell_signals = []
    
    # RSI Topvorming
    rsi = RSIIndicator(df['close'])
    rsi_values = rsi.rsi()
    if rsi_values.iloc[-2] > 70 and rsi_values.iloc[-1] < rsi_values.iloc[-2]:
        sell_signals.append("RSI daalt van >70: Momentumverlies")
    
    # MACD Bearish Crossover
    macd = MACD(df['close'])
    macd_line = macd.macd()
    signal_line = macd.macd_signal()
    if macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
        sell_signals.append("MACD kruist onder signaallijn: Bearish shift")
    
    # Prijs onder MA50
    ma50 = df['close'].rolling(window=50).mean()
    if current_price < ma50.iloc[-1]:
        sell_signals.append("Prijs onder MA50: Trendbreuk")
    
    # Trailing Stop Logica (10% onder hoogste prijs laatste 20 dagen)
    highest_price = df['high'].rolling(window=20).max().iloc[-1]
    if current_price < highest_price * 0.9:
        sell_signals.append("Prijs >10% onder hoogste punt: Stop-loss")
    
    # Take Profit (>20% boven gemiddelde 10-daagse low)
    avg_low = df['low'].rolling(window=10).mean().iloc[-1]
    if current_price > avg_low * 1.2:
        sell_signals.append("Prijs >20% boven gemiddelde low: Winst nemen")
    
    return sell_signals

def run_golden_cross_screener():
    """Run the Golden Cross screener"""
    print("Start Golden Cross screener...")
    
    # Initialize exchange
    exchange = get_exchange()
    if not exchange:
        print("Kon geen verbinding maken met de exchange. Script wordt afgebroken.")
        return

    # Get symbols
    symbols = get_top_100_binance_symbols()
    matches = []

    # Strategy parameters
    strategy_name = "Golden Cross"
    description = "MA50 kruist boven MA200: mogelijk start van een nieuwe uptrend."

    # Analyze each symbol
    for symbol in symbols:
        print(f"\nAnalyseren van {symbol}...")
        try:
            df = fetch_ohlcv_with_retry(exchange, symbol)
            if df is None or df.empty:
                continue

            close = df["close"]
            current_price = close.iloc[-1]

            # Calculate Moving Averages
            ma50 = close.rolling(window=50).mean()
            ma200 = close.rolling(window=200).mean()
            
            if not pd.isna(ma50.iloc[-1]) and not pd.isna(ma200.iloc[-1]):
                if ma50.iloc[-1] > ma200.iloc[-1] and ma50.iloc[-2] <= ma200.iloc[-2]:
                    # Analyze sell signals for matches
                    sell_signals = analyze_sell_signals(df, current_price)
                    matches.append((symbol, current_price, sell_signals))
                    print(f"Match gevonden! Prijs: ${current_price:.2f}")
                    if sell_signals:
                        print("Verkoopsignalen:")
                        for signal in sell_signals:
                            print(f"- {signal}")

            # Add a small delay between symbols
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"Fout bij {symbol}: {e}")

    # Generate dashboard
    if matches:
        bestandsnaam = generate_html_dashboard(matches, strategy_name, description)
        print(f"\n✅ Screener voltooid – resultaten opgeslagen in: {bestandsnaam}")
        print(f"📊 Aantal matches gevonden: {len(matches)}")
    else:
        print("\n❌ Geen matches gevonden voor deze strategie.")

if __name__ == "__main__":
    run_golden_cross_screener() 