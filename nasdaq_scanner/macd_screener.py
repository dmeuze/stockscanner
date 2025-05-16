from nasdaq_base import run_screener, generate_dashboard

def macd_strategy(df, symbol):
    """MACD strategie: zoek naar aandelen waar de MACD-lijn boven de signaallijn kruist"""
    if df is None or df.empty or len(df) < 2:
        return None
    
    # Check of de MACD-lijn boven de signaallijn kruist
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['Signal'].iloc[-1]
    prev_macd = df['MACD'].iloc[-2]
    prev_signal = df['Signal'].iloc[-2]
    
    if prev_macd < prev_signal and last_macd > last_signal:
        return generate_dashboard(df, symbol, "MACD Crossover")
    return None

def run_macd_screener():
    """Voer de MACD screener uit"""
    return run_screener(macd_strategy)

if __name__ == "__main__":
    run_macd_screener() 