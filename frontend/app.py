"""
KIVerdienst v2 - Frontend Application
Flask web interface
"""
from flask import Flask, render_template, jsonify, request
import requests
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')

def api_request(endpoint, method='GET', data=None):
    """Helper function to make API requests"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        logger.info(f"API Request: {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {'success': False, 'error': str(e)}

# Routes
@app.route('/')
def index():
    """Landing page"""
    try:
        # Check setup status
        setup_status = api_request('/api/setup/status')
        
        if setup_status.get('success') and not setup_status.get('data', {}).get('completed'):
            return render_template('setup/welcome.html')
        
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/brands')
def brands():
    """Brand management page"""
    return render_template('brands.html')

@app.route('/videos')
def videos():
    """Video library page"""
    return render_template('videos.html')

@app.route('/characters')
def characters():
    """Character management page"""
    return render_template('characters.html')

@app.route('/content')
def content():
    """Content strategy page"""
    return render_template('content.html')

@app.route('/debug')
def debug():
    """Debug and monitoring page"""
    return render_template('debug.html')

# Setup wizard routes
@app.route('/setup')
def setup_welcome():
    """Setup wizard welcome"""
    return render_template('setup/welcome.html')

@app.route('/setup/database')
def setup_database():
    """Setup database configuration"""
    return render_template('setup/database.html')

@app.route('/setup/system')
def setup_system():
    """Setup system configuration"""
    return render_template('setup/system.html')

@app.route('/setup/complete')
def setup_complete():
    """Setup completion"""
    return render_template('setup/complete.html')

# API proxy endpoints (for frontend JavaScript)
@app.route('/proxy/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    """Proxy API requests to backend"""
    try:
        data = request.get_json() if request.method in ['POST', 'PUT'] else None
        result = api_request(f'/api/{endpoint}', method=request.method, data=data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('dashboard.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('dashboard.html'), 500

if __name__ == '__main__':
    port = int(os.getenv('FRONTEND_PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting KIVerdienst v2 Frontend on port {port}")
    logger.info(f"Backend API: {BACKEND_URL}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
