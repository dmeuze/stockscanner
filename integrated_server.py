from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, session
from flask_cors import CORS
import os
from datetime import datetime
import json
import glob
import urllib.parse
import time

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here'  # Voor session management

# Import both scanner modules
from crypto_scanner.crypto_screener import run_screener as run_crypto_screener
from nasdaq_scanner.nasdaq_screener import run_screener as run_nasdaq_screener

CRYPTO_STRATEGIES = [
    ("rsi", "RSI Oversold"),
    ("bollinger", "Bollinger Bounce"),
    ("macd", "MACD Crossover"),
    ("ma", "Trendvolgend (MA)"),
    ("volume", "Volume Spike"),
    ("golden_cross", "Golden Cross")
]
NASDAQ_STRATEGIES = CRYPTO_STRATEGIES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crypto')
def crypto_strategies():
    return render_template('strategies.html', scanner_type='crypto')

@app.route('/nasdaq')
def nasdaq_strategies():
    return render_template('strategies.html', scanner_type='nasdaq')

@app.route('/run/<scanner_type>/<strategy>')
def run_strategy(scanner_type, strategy):
    timeframe = request.args.get('timeframe', '1d')
    # Toon eerst de processing pagina en start daarna de scan
    return render_template('processing.html') + f"<script>setTimeout(function(){{window.location.href='/do_scan/{scanner_type}/{strategy}?timeframe={timeframe}';}}, 500);</script>"

@app.route('/do_scan/<scanner_type>/<strategy>')
def do_scan(scanner_type, strategy):
    try:
        symbols = request.args.get('symbols')
        if symbols:
            symbols = [s.strip() for s in symbols.split(',') if s.strip()]
        else:
            symbols = None
        timeframe = request.args.get('timeframe', '1d')
        if scanner_type == 'crypto':
            results = run_crypto_screener(strategy, symbols=symbols, timeframe=timeframe)
        elif scanner_type == 'nasdaq':
            results = run_nasdaq_screener(strategy, symbols=symbols, timeframe=timeframe)
        else:
            return render_template('results.html', strategieen={}, scanner_type=scanner_type, strategy=strategy, status='error', message='Ongeldige scanner type')

        if results is None:
            return render_template('results.html', strategieen={}, scanner_type=scanner_type, strategy=strategy, status='error', message='Er is een fout opgetreden bij het uitvoeren van de scan')

        return render_template('results.html', strategieen=results, scanner_type=scanner_type, strategy=strategy, status='success', message='Scan succesvol voltooid!')
    except Exception as e:
        return render_template('results.html', strategieen={}, scanner_type=scanner_type, strategy=strategy, status='error', message=f'Er is een fout opgetreden: {str(e)}')

@app.route('/refresh/<scanner_type>/<strategy>')
def refresh_strategy(scanner_type, strategy):
    # Toon eerst de processing pagina en start daarna de scan opnieuw
    return render_template('processing.html') + f"<script>setTimeout(function(){{window.location.href='/do_scan/{scanner_type}/{strategy}';}}, 500);</script>"

@app.route('/results/<path:filename>')
def serve_results(filename):
    return send_from_directory('results', filename)

@app.route('/results/<scanner_type>')
def get_results(scanner_type):
    try:
        results = []
        pattern = f"{scanner_type}_*.json"
        
        # Zoek alle JSON bestanden in de results directory
        for filename in os.listdir('results'):
            if filename.startswith(f"{scanner_type}_") and filename.endswith('.json'):
                filepath = os.path.join('results', filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Voeg timestamp toe uit bestandsnaam
                    timestamp = filename.split('_')[1].split('.')[0]
                    results.append({
                        'timestamp': timestamp,
                        'data': data
                    })
        
        # Sorteer op timestamp (nieuwste eerst)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Neem de laatste 10 resultaten
        return jsonify(results[:10])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results_list/<scanner_type>')
def results_list(scanner_type):
    # Zoek alle JSON bestanden in de results directory voor het type
    files = []
    for filename in os.listdir('results'):
        if filename.startswith(f"{scanner_type}_") and filename.endswith('.json'):
            # Extract timestamp from filename
            parts = filename.split('_')
            if len(parts) >= 3:
                timestamp = parts[-1].replace('.json', '')
            else:
                timestamp = ''
            files.append({'filename': filename, 'timestamp': timestamp})
    # Sorteer op timestamp (nieuwste eerst)
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('results_list.html', scanner_type=scanner_type, results=files)

if __name__ == '__main__':
    print("Server starten op http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000) 