from nasdaq_base import run_screener, generate_dashboard

def ma_strategy(df, symbol):
    """Moving Average strategie: zoek naar aandelen in een gezonde uptrend"""
    if df is None or df.empty:
        return None
    
    # Check of MA50 boven MA200 is en prijs boven MA50
    last_close = df['Close'].iloc[-1]
    last_ma50 = df['MA50'].iloc[-1]
    last_ma200 = df['MA200'].iloc[-1]
    
    if last_ma50 > last_ma200 and last_close > last_ma50:
        return generate_dashboard(df, symbol, "Trendvolgend (MA)")
    return None

def run_ma_screener():
    """Voer de Moving Average screener uit"""
    return run_screener(ma_strategy)

if __name__ == "__main__":
    run_ma_screener() 