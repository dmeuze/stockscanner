from datetime import datetime
import os
import glob

def generate_index_page():
    """Generate the main index page with links to all strategy results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get all dashboard files
    dashboard_files = glob.glob("*_dashboard_*.html")
    dashboard_files.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time
    
    # Group files by strategy
    strategies = {
        "RSI Oversold": [],
        "Bollinger Bounce": [],
        "MACD Crossover": [],
        "Trendvolgend (MA)": [],
        "Golden Cross": []
    }
    
    for file in dashboard_files:
        for strategy in strategies.keys():
            if strategy.lower().replace(' ', '_') in file.lower():
                strategies[strategy].append(file)
    
    # JavaScript code as a separate string
    js_code = '''\
    async function runStrategy(script, button) {
        const originalText = button.textContent;
        const strategy = script.replace('_screener.py', '');
        const statusDiv = document.getElementById(`${strategy}-status`);
        
        // Reset and show running status
        button.disabled = true;
        button.textContent = 'Running...';
        statusDiv.textContent = 'Screener wordt uitgevoerd...';
        statusDiv.className = 'status-message running';
        
        try {
            const response = await fetch(`/run/${strategy}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.error) {
                console.error('Server error:', data.error);
                statusDiv.textContent = `Error: ${data.error}`;
                statusDiv.className = 'status-message error';
            } else {
                console.log('Server output:', data.output);
                statusDiv.textContent = 'Screener succesvol uitgevoerd!';
                statusDiv.className = 'status-message success';
                
                // Wacht 2 seconden voordat we de pagina verversen
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            statusDiv.textContent = `Error: ${error.message}`;
            statusDiv.className = 'status-message error';
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    '''

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto Screener - Overzicht</title>
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
            .strategy-section {{
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }}
            .strategy-title {{
                color: #007bff;
                margin-bottom: 15px;
                font-size: 1.2em;
                font-weight: bold;
            }}
            .strategy-description {{
                color: #666;
                margin-bottom: 15px;
                font-style: italic;
            }}
            .result-list {{
                list-style: none;
                padding: 0;
            }}
            .result-item {{
                margin: 10px 0;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .result-link {{
                color: #28a745;
                text-decoration: none;
                font-weight: bold;
            }}
            .result-link:hover {{
                text-decoration: underline;
            }}
            .run-button {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
                transition: background-color 0.3s;
            }}
            .run-button:hover {{
                background-color: #0056b3;
            }}
            .timestamp {{
                text-align: center;
                color: #666;
                margin-top: 30px;
                font-size: 0.9em;
            }}
            .status-message {{
                margin-top: 10px;
                padding: 10px;
                border-radius: 5px;
                display: none;
            }}
            .status-message.running {{
                display: block;
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeeba;
            }}
            .status-message.success {{
                display: block;
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .status-message.error {{
                display: block;
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Crypto Screener - Overzicht</h1>
            
            <div class="strategy-section">
                <div class="strategy-title">RSI Oversold</div>
                <div class="strategy-description">RSI onder 30: mogelijk oversold en kans op reversal.</div>
                <button class="run-button" onclick="runStrategy('rsi_screener.py', this)">Run RSI Screener</button>
                <div id="rsi-status" class="status-message"></div>
                <ul class="result-list">
                    {''.join(f'<li class="result-item"><a href="/results/{file}" class="result-link">{file}</a></li>' for file in strategies["RSI Oversold"])}
                </ul>
            </div>
            
            <div class="strategy-section">
                <div class="strategy-title">Bollinger Bounce</div>
                <div class="strategy-description">Koers onder onderste Bollinger Band: kans op pullback reversal.</div>
                <button class="run-button" onclick="runStrategy('bollinger_screener.py', this)">Run Bollinger Screener</button>
                <div id="bollinger-status" class="status-message"></div>
                <ul class="result-list">
                    {''.join(f'<li class="result-item"><a href="/results/{file}" class="result-link">{file}</a></li>' for file in strategies["Bollinger Bounce"])}
                </ul>
            </div>
            
            <div class="strategy-section">
                <div class="strategy-title">MACD Crossover</div>
                <div class="strategy-description">MACD-lijn kruist boven signaallijn: momentum komt terug.</div>
                <button class="run-button" onclick="runStrategy('macd_screener.py', this)">Run MACD Screener</button>
                <div id="macd-status" class="status-message"></div>
                <ul class="result-list">
                    {''.join(f'<li class="result-item"><a href="/results/{file}" class="result-link">{file}</a></li>' for file in strategies["MACD Crossover"])}
                </ul>
            </div>
            
            <div class="strategy-section">
                <div class="strategy-title">Trendvolgend (MA)</div>
                <div class="strategy-description">MA50 boven MA200 en prijs boven MA50: gezonde uptrend.</div>
                <button class="run-button" onclick="runStrategy('ma_screener.py', this)">Run MA Screener</button>
                <div id="ma-status" class="status-message"></div>
                <ul class="result-list">
                    {''.join(f'<li class="result-item"><a href="/results/{file}" class="result-link">{file}</a></li>' for file in strategies["Trendvolgend (MA)"])}
                </ul>
            </div>
            
            <div class="strategy-section">
                <div class="strategy-title">Golden Cross</div>
                <div class="strategy-description">MA50 kruist boven MA200: mogelijk start van een nieuwe uptrend.</div>
                <button class="run-button" onclick="runStrategy('golden_cross_screener.py', this)">Run Golden Cross Screener</button>
                <div id="golden_cross-status" class="status-message"></div>
                <ul class="result-list">
                    {''.join(f'<li class="result-item"><a href="/results/{file}" class="result-link">{file}</a></li>' for file in strategies["Golden Cross"])}
                </ul>
            </div>
            
            <p class="timestamp">Laatste update: {timestamp}</p>
        </div>

        <script>
        {js_code}
        </script>
    </body>
    </html>
    """
    
    return html_template

if __name__ == "__main__":
    with open('index.html', 'w') as f:
        f.write(generate_index_page()) 