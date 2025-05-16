from nasdaq_base import run_screener, generate_dashboard

def golden_cross_strategy(df, symbol):
    """Golden Cross strategie: zoek naar aandelen waar MA50 boven MA200 kruist"""
    if df is None or df.empty or len(df) < 2:
        return None
    
    # Check of MA50 boven MA200 kruist
    last_ma50 = df['MA50'].iloc[-1]
    last_ma200 = df['MA200'].iloc[-1]
    prev_ma50 = df['MA50'].iloc[-2]
    prev_ma200 = df['MA200'].iloc[-2]
    
    if prev_ma50 < prev_ma200 and last_ma50 > last_ma200:
        return generate_dashboard(df, symbol, "Golden Cross")
    return None

def run_golden_cross_screener():
    """Voer de Golden Cross screener uit"""
    return run_screener(golden_cross_strategy)

if __name__ == "__main__":
    run_golden_cross_screener() 