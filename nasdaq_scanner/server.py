from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
from index import generate_index_page
from rsi_screener import run_rsi_screener
from bollinger_screener import run_bollinger_screener
from macd_screener import run_macd_screener
from ma_screener import run_ma_screener
from golden_cross_screener import run_golden_cross_screener

app = Flask(__name__)
CORS(app)

# Verander naar de directory van het script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    """Generate and return the index page"""
    return generate_index_page()

@app.route('/run/<strategy>')
def run_strategy(strategy):
    """Run the specified strategy screener"""
    try:
        if strategy == 'rsi':
            run_rsi_screener()
        elif strategy == 'bollinger':
            run_bollinger_screener()
        elif strategy == 'macd':
            run_macd_screener()
        elif strategy == 'ma':
            run_ma_screener()
        elif strategy == 'golden_cross':
            run_golden_cross_screener()
        else:
            return jsonify({'error': f'Unknown strategy: {strategy}'}), 400
        
        return jsonify({'output': f'Strategy {strategy} completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def get_results(filename):
    """Serve the results HTML file"""
    try:
        return send_file(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server is running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', debug=True) 