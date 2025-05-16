from nasdaq_base import run_screener, generate_dashboard

def bollinger_strategy(df, symbol):
    """Bollinger Bands strategie: zoek naar aandelen onder de onderste band"""
    if df is None or df.empty:
        return None
    
    # Check of de laatste prijs onder de onderste band is
    last_close = df['Close'].iloc[-1]
    last_lower_band = df['LowerBand'].iloc[-1]
    
    if last_close < last_lower_band:
        return generate_dashboard(df, symbol, "Bollinger Bounce")
    return None

def run_bollinger_screener():
    """Voer de Bollinger Bands screener uit"""
    return run_screener(bollinger_strategy)

if __name__ == "__main__":
    run_bollinger_screener() 