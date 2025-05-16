import ccxt
import pandas as pd
from datetime import datetime
from jinja2 import Template
import time
import random
import requests

def get_exchange():
    """Initialize and return the exchange with error handling"""
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 30000,
        })
        return exchange
    except Exception as e:
        print(f"Fout bij initialiseren exchange: {e}")
        return None

def get_top_100_binance_symbols():
    """Haalt de top 100 coins van CoinGecko en filtert op Binance USDT-markten."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        symbols = []
        for coin in data:
            symbol = coin["symbol"].upper()
            binance_symbol = f"{symbol}/USDT"
            symbols.append(binance_symbol)
        print(f"Top 100 coins geladen van CoinGecko: {len(symbols)} stuks.")
        return symbols
    except Exception as e:
        print(f"Fout bij ophalen top 100 coins: {e}")
        return []

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

def generate_html_dashboard(matches, strategy_name, description):
    """Generate HTML dashboard with results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bestandsnaam = f"{strategy_name.lower().replace(' ', '_')}_dashboard_{timestamp.split()[0]}.html"
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto Screener - {strategy_name}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            .description {{
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-style: italic;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .price {{
                font-weight: bold;
                color: #28a745;
            }}
            .sell-signals {{
                color: #dc3545;
                font-size: 0.9em;
            }}
            .sell-signal-item {{
                margin: 5px 0;
                padding: 5px;
                background-color: #fff3f3;
                border-left: 3px solid #dc3545;
            }}
            .timestamp {{
                text-align: center;
                color: #666;
                margin-top: 30px;
                font-size: 0.9em;
            }}
            .refresh-container {{
                text-align: center;
                margin: 20px 0;
            }}
            .refresh-button {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            }}
            .refresh-button:hover {{
                background-color: #0056b3;
            }}
            .refresh-button:disabled {{
                background-color: #ccc;
                cursor: not-allowed;
            }}
            .auto-refresh {{
                margin-left: 10px;
                color: #666;
            }}
            .auto-refresh input {{
                margin-right: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Crypto Screener - {strategy_name}</h1>
            <p class="description">{description}</p>
            
            <div class="refresh-container">
                <button class="refresh-button" onclick="refreshData()">Ververs Data</button>
                <span class="auto-refresh">
                    <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()">
                    <label for="autoRefresh">Auto verversen elke 5 minuten</label>
                </span>
            </div>
            
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Huidige Prijs</th>
                    <th>Verkoopsignalen</th>
                </tr>
                {''.join(f"""
                <tr>
                    <td>{symbol}</td>
                    <td class="price">${price:.2f}</td>
                    <td class="sell-signals">
                        {''.join(f'<div class="sell-signal-item">{signal}</div>' for signal in (signals or [])) if signals else 'Geen verkoopsignalen'}
                    </td>
                </tr>
                """ for symbol, price, signals in matches)}
            </table>
            
            <p class="timestamp" id="lastUpdate">Laatste update: {timestamp}</p>
        </div>

        <script>
            let autoRefreshInterval = null;
            
            function updateTimestamp() {{
                const now = new Date();
                const timestamp = now.toLocaleString('nl-NL');
                document.getElementById('lastUpdate').textContent = 'Laatste update: ' + timestamp;
            }}
            
            function refreshData() {{
                const button = document.querySelector('.refresh-button');
                button.disabled = true;
                button.textContent = 'Verversen...';
                
                // Simuleer een refresh door de pagina te herladen
                setTimeout(() => {{
                    window.location.reload();
                }}, 1000);
            }}
            
            function toggleAutoRefresh() {{
                const checkbox = document.getElementById('autoRefresh');
                if (checkbox.checked) {{
                    // Start auto-refresh elke 5 minuten
                    autoRefreshInterval = setInterval(refreshData, 5 * 60 * 1000);
                }} else {{
                    // Stop auto-refresh
                    if (autoRefreshInterval) {{
                        clearInterval(autoRefreshInterval);
                        autoRefreshInterval = null;
                    }}
                }}
            }}
            
            // Update timestamp elke seconde
            setInterval(updateTimestamp, 1000);
        </script>
    </body>
    </html>
    """
    
    with open(bestandsnaam, 'w') as f:
        f.write(html_template)
    
    return bestandsnaam 