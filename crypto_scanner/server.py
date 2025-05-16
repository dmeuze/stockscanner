from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from index import generate_index_page
from ma_screener import run_ma_screener
from macd_screener import run_macd_screener
from rsi_screener import run_rsi_screener
from golden_cross_screener import run_golden_cross_screener
from bollinger_screener import run_bollinger_screener

app = Flask(__name__)
CORS(app)

# Zorg ervoor dat we in de juiste directory werken
os.chdir(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    return generate_index_page()

@app.route('/run/<strategy>')
def run_strategy(strategy):
    try:
        if strategy == 'ma':
            run_ma_screener()
        elif strategy == 'macd':
            run_macd_screener()
        elif strategy == 'rsi':
            run_rsi_screener()
        elif strategy == 'golden_cross':
            run_golden_cross_screener()
        elif strategy == 'bollinger':
            run_bollinger_screener()
        else:
            return jsonify({'error': 'Ongeldige strategie'}), 400
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def get_results(filename):
    try:
        return send_file(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server is running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', debug=True) 