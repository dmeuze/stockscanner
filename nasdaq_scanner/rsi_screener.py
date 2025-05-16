from nasdaq_base import run_screener, generate_dashboard

def rsi_strategy(df, symbol):
    """RSI strategie: zoek naar aandelen met RSI onder 30 (oversold)"""
    if df is None or df.empty:
        return None
    
    # Check of de laatste RSI onder 30 is
    last_rsi = df['RSI'].iloc[-1]
    if last_rsi < 30:
        return generate_dashboard(df, symbol, "RSI Oversold")
    return None

def run_rsi_screener():
    """Voer de RSI screener uit"""
    return run_screener(rsi_strategy)

if __name__ == "__main__":
    run_rsi_screener() 