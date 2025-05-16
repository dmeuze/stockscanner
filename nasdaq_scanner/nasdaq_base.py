import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def get_nasdaq_symbols():
    """Haal alle NASDAQ symbolen op"""
    # Download NASDAQ symbolen van nasdaq.com
    nasdaq = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]
    symbols = nasdaq['Ticker'].tolist()
    return symbols

def get_stock_data(symbol, period='1y', interval='1d'):
    """Haal historische data op voor een aandeel"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error getting data for {symbol}: {str(e)}")
        return None

def calculate_indicators(df):
    """Bereken technische indicatoren voor de data"""
    if df is None or df.empty:
        return None
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['UpperBand'] = df['MA20'] + (df['STD20'] * 2)
    df['LowerBand'] = df['MA20'] - (df['STD20'] * 2)
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Moving Averages
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    return df

def generate_dashboard(df, symbol, strategy_name):
    """Genereer een HTML dashboard voor een aandeel"""
    if df is None or df.empty:
        return None
    
    # Maak een timestamp voor de bestandsnaam
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{strategy_name.lower().replace(' ', '_')}_dashboard_{timestamp}.html"
    
    # Bereken laatste waarden
    last_close = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['Signal'].iloc[-1]
    last_ma50 = df['MA50'].iloc[-1]
    last_ma200 = df['MA200'].iloc[-1]
    
    # Genereer HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{symbol} - {strategy_name}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }}
            .info-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .info-card {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }}
            .info-label {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }}
            .info-value {{
                color: #333;
                font-size: 1.2em;
                font-weight: bold;
            }}
            .chart-container {{
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{symbol} - {strategy_name}</h1>
            
            <div class="info-section">
                <div class="info-card">
                    <div class="info-label">Laatste koers</div>
                    <div class="info-value">${last_close:.2f}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">RSI (14)</div>
                    <div class="info-value">{last_rsi:.2f}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">MACD</div>
                    <div class="info-value">{last_macd:.2f}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Signal</div>
                    <div class="info-value">{last_signal:.2f}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">MA50</div>
                    <div class="info-value">${last_ma50:.2f}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">MA200</div>
                    <div class="info-value">${last_ma200:.2f}</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div id="price-chart"></div>
            </div>
        </div>

        <script>
            // Data voor de grafiek
            const dates = {df.index.strftime('%Y-%m-%d').tolist()};
            const closes = {df['Close'].tolist()};
            const ma50 = {df['MA50'].tolist()};
            const ma200 = {df['MA200'].tolist()};
            const upperBand = {df['UpperBand'].tolist()};
            const lowerBand = {df['LowerBand'].tolist()};
            
            // Maak de prijsgrafiek
            const priceTrace = {{
                x: dates,
                y: closes,
                type: 'scatter',
                mode: 'lines',
                name: 'Prijs',
                line: {{color: '#17BECF'}}
            }};
            
            const ma50Trace = {{
                x: dates,
                y: ma50,
                type: 'scatter',
                mode: 'lines',
                name: 'MA50',
                line: {{color: '#FF7F0E'}}
            }};
            
            const ma200Trace = {{
                x: dates,
                y: ma200,
                type: 'scatter',
                mode: 'lines',
                name: 'MA200',
                line: {{color: '#2CA02C'}}
            }};
            
            const upperBandTrace = {{
                x: dates,
                y: upperBand,
                type: 'scatter',
                mode: 'lines',
                name: 'Upper Band',
                line: {{color: '#D62728', dash: 'dash'}}
            }};
            
            const lowerBandTrace = {{
                x: dates,
                y: lowerBand,
                type: 'scatter',
                mode: 'lines',
                name: 'Lower Band',
                line: {{color: '#D62728', dash: 'dash'}}
            }};
            
            const layout = {{
                title: '{symbol} Prijsgrafiek',
                xaxis: {{title: 'Datum'}},
                yaxis: {{title: 'Prijs ($)'}},
                showlegend: true,
                legend: {{x: 0, y: 1}}
            }};
            
            Plotly.newPlot('price-chart', [priceTrace, ma50Trace, ma200Trace, upperBandTrace, lowerBandTrace], layout);
        </script>
    </body>
    </html>
    """
    
    # Schrijf het dashboard naar een bestand
    with open(filename, 'w') as f:
        f.write(html)
    
    return filename

def run_screener(strategy_function):
    """Voer een screener uit met de gegeven strategie functie"""
    symbols = get_nasdaq_symbols()
    results = []
    
    for symbol in symbols:
        df = get_stock_data(symbol)
        if df is not None:
            df = calculate_indicators(df)
            if df is not None:
                result = strategy_function(df, symbol)
                if result:
                    results.append(result)
    
    return results 