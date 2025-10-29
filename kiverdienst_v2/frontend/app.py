"""
KIVerdienst v2 - Flask Frontend
Web interface for system management
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')


def make_api_request(endpoint, method='GET', data=None):
    """
    Helper function to make API requests to backend
    """
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return None, f"Unsupported method: {method}"
        
        if response.status_code >= 400:
            return None, f"API Error: {response.status_code}"
        
        return response.json(), None
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None, str(e)


@app.route('/')
def index():
    """Root route - redirect to setup or dashboard"""
    # Check if setup is completed
    data, error = make_api_request('/api/setup/status')
    
    if error:
        return render_template('error.html', error=error)
    
    if data and data.get('completed'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('setup'))


@app.route('/setup')
def setup():
    """Setup wizard page"""
    return render_template('setup.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    # Check if setup is completed
    setup_data, error = make_api_request('/api/setup/status')
    
    if error or not setup_data.get('completed'):
        return redirect(url_for('setup'))
    
    # Get system stats
    stats_data, _ = make_api_request('/api/system/stats')
    health_data, _ = make_api_request('/api/system/health')
    
    return render_template(
        'dashboard.html',
        stats=stats_data or {},
        health=health_data or {}
    )


@app.route('/brands')
def brands():
    """Brands management page"""
    # Get all brands
    brands_data, error = make_api_request('/api/brands')
    
    if error:
        brands_data = []
    
    return render_template('brands.html', brands=brands_data)


@app.route('/debug')
def debug():
    """Debug and troubleshooting page"""
    # Get system health
    health_data, _ = make_api_request('/api/system/health')
    
    # Get Docker status
    docker_data, _ = make_api_request('/api/system/docker')
    
    # Get port status
    ports_data, _ = make_api_request('/api/debug/ports')
    
    # Get database info
    db_data, _ = make_api_request('/api/debug/database')
    
    return render_template(
        'debug.html',
        health=health_data or {},
        docker=docker_data or {},
        ports=ports_data or {},
        database=db_data or {}
    )


@app.route('/logs')
def logs():
    """System logs viewer page"""
    # Get available components
    components_data, _ = make_api_request('/api/debug/components')
    
    return render_template(
        'logs.html',
        components=components_data.get('components', []) if components_data else []
    )


# API proxy endpoints for AJAX requests
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def api_proxy(path):
    """
    Proxy API requests to backend
    This allows frontend JavaScript to make API calls
    """
    endpoint = f"/api/{path}"
    
    # Get query parameters
    if request.args:
        query_string = '&'.join([f"{k}={v}" for k, v in request.args.items()])
        endpoint += f"?{query_string}"
    
    # Get request data
    data = request.get_json() if request.is_json else None
    
    # Make API request
    result, error = make_api_request(endpoint, method=request.method, data=data)
    
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify(result)


@app.template_filter('datetime')
def format_datetime(value):
    """Template filter to format datetime strings"""
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        return value
    except:
        return value


@app.template_filter('timeago')
def time_ago(value):
    """Template filter to show relative time"""
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            diff = now - dt
            
            seconds = diff.total_seconds()
            
            if seconds < 60:
                return "gerade eben"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f"vor {minutes} Minute{'n' if minutes > 1 else ''}"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"vor {hours} Stunde{'n' if hours > 1 else ''}"
            else:
                days = int(seconds / 86400)
                return f"vor {days} Tag{'en' if days > 1 else ''}"
        return value
    except:
        return value


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('error.html', error="Seite nicht gefunden"), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    return render_template('error.html', error="Interner Serverfehler"), 500


if __name__ == '__main__':
    logger.info("Starting KIVerdienst v2 Frontend...")
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FRONTEND_PORT', 5000)),
        debug=os.getenv('DEBUG', 'false').lower() == 'true'
    )
