from crypto_base import get_exchange, get_top_100_binance_symbols, fetch_ohlcv_with_retry, generate_html_dashboard
import pandas as pd
import time
import random

def run_volume_screener():
    """Run the Volume Spike screener"""
    print("Start Volume Spike screener...")
    
    # Initialize exchange
    exchange = get_exchange()
    if not exchange:
        print("Kon geen verbinding maken met de exchange. Script wordt afgebroken.")
        return

    # Load markets
    print("Laden van Binance markten...")
    try:
        exchange.load_markets()
        print(f"Aantal beschikbare markten: {len(exchange.markets)}")
    except Exception as e:
        print(f"Fout bij laden markten: {e}")
        return

    # Get symbols
    symbols = get_top_100_binance_symbols()
    matches = []
    processed_count = 0
    skipped_count = 0

    # Strategy parameters
    strategy_name = "Volume Spike"
    description = "Volume is > 1.3x het 30-daags gemiddelde: mogelijk institutionele aankoop."
    volume_threshold = 1.3

    # Analyze each symbol
    for symbol in symbols:
        try:
            # Check if symbol exists on Binance
            if not exchange.has['fetchOHLCV'] or not exchange.market(symbol):
                print(f"Slaat {symbol} over - niet beschikbaar op Binance")
                skipped_count += 1
                continue

            print(f"\nAnalyseren van {symbol}...")
            df = fetch_ohlcv_with_retry(exchange, symbol)
            if df is None or df.empty:
                skipped_count += 1
                continue

            close = df["close"]
            volume = df["volume"]
            current_price = close.iloc[-1]

            # Calculate Volume Spike
            avg_vol = volume.rolling(window=30).mean().iloc[-2]
            if not pd.isna(avg_vol) and volume.iloc[-1] > avg_vol * volume_threshold:
                matches.append((symbol, current_price, round(volume.iloc[-1], 0)))
                print(f"Match gevonden! Prijs: ${current_price:.2f}")

            processed_count += 1
            print(f"Voortgang: {processed_count} verwerkt, {skipped_count} overgeslagen")

            # Add a small delay between symbols
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"Fout bij {symbol}: {e}")
            skipped_count += 1
            continue

    # Generate dashboard
    if matches:
        bestandsnaam = generate_html_dashboard(matches, strategy_name, description)
        print(f"\n✅ Screener voltooid – resultaten opgeslagen in: {bestandsnaam}")
        print(f"📊 Aantal matches gevonden: {len(matches)}")
        print(f"📈 Totaal verwerkt: {processed_count}")
        print(f"⏭️ Overgeslagen: {skipped_count}")
    else:
        print("\n❌ Geen matches gevonden voor deze strategie.")
        print(f"📈 Totaal verwerkt: {processed_count}")
        print(f"⏭️ Overgeslagen: {skipped_count}")

if __name__ == "__main__":
    run_volume_screener() 