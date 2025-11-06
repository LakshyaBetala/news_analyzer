"""
News Credibility Analyzer - Main Application
Real-time news credibility analysis using keyword-based scoring.
Designed to be extensible with transformer models.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
import os
import sys

# Handle both relative and absolute imports
try:
    from .model import NewsCredibilityAnalyzer
except ImportError:
    # Fallback for direct execution (python app/main.py)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.model import NewsCredibilityAnalyzer

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize analyzer
analyzer = NewsCredibilityAnalyzer()

# Version from environment or default
VERSION = os.getenv('APP_VERSION', '1.0.0')


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html', version=VERSION)


@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """
    Analyze news article for credibility.
    
    Expected JSON payload:
    {
        "title": "Article title",
        "content": "Article content",
        "source": "Source name (optional)"
    }
    
    Returns:
    {
        "credibility_score": float (0-100),
        "risk_factors": list,
        "recommendations": list,
        "timestamp": ISO datetime,
        "version": str
    }
    """
    try:
        # Try to get JSON data
        # If Content-Type is not application/json, force=True will try to parse anyway
        data = request.get_json(force=True, silent=True)
        
        # If data is None, it means JSON parsing failed or no data was sent
        if data is None:
            # Check if there's any data in the request
            if request.data:
                # There's data but it's not valid JSON
                return jsonify({
                    'error': 'Invalid JSON format',
                    'version': VERSION
                }), 400
            else:
                # No data at all
                return jsonify({
                    'error': 'No JSON data provided',
                    'version': VERSION
                }), 400
        
        title = data.get('title', '')
        content = data.get('content', '')
        source = data.get('source', '')
        
        if not title and not content:
            return jsonify({
                'error': 'Title or content is required',
                'version': VERSION
            }), 400
        
        # Analyze credibility
        result = analyzer.analyze(title, content, source)
        
        # Add metadata
        result['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        result['version'] = VERSION
        
        return jsonify(result), 200
        
    except Exception as e:
        # Other errors
        return jsonify({
            'error': str(e),
            'version': VERSION
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': VERSION,
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }), 200


@app.route('/api/version', methods=['GET'])
def version():
    """Version endpoint."""
    return jsonify({
        'version': VERSION,
        'service': 'news-credibility-analyzer'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

