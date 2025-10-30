"""
Frontend Flask application for KIVerdienst v2.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
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

def call_api(endpoint, method='GET', data=None):
    """Helper function to call backend API."""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return {'success': False, 'error': 'Invalid method'}
        
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return {'success': False, 'error': str(e)}

# ----- MAIN ROUTES -----

@app.route('/')
def index():
    """Landing page - check setup status and redirect."""
    try:
        setup_status = call_api('/api/setup/status')
        
        if setup_status.get('success') and setup_status.get('data', {}).get('completed'):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('setup_welcome'))
    except:
        return redirect(url_for('setup_welcome'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard."""
    try:
        stats = call_api('/api/system/stats')
        brands = call_api('/api/brands')
        recent_videos = call_api('/api/videos?limit=10')
        
        return render_template('dashboard.html',
                             stats=stats.get('data', {}),
                             brands=brands.get('data', []),
                             recent_videos=recent_videos.get('data', []))
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html', 
                             stats={}, brands=[], recent_videos=[])

# ----- SETUP WIZARD -----

@app.route('/setup/welcome')
def setup_welcome():
    """Setup wizard - welcome page."""
    return render_template('setup/welcome.html')

@app.route('/setup/database')
def setup_database():
    """Setup wizard - database configuration."""
    return render_template('setup/database.html')

@app.route('/setup/system')
def setup_system():
    """Setup wizard - system configuration."""
    return render_template('setup/system.html')

@app.route('/setup/complete')
def setup_complete():
    """Setup wizard - completion page."""
    return render_template('setup/complete.html')

# ----- BRAND MANAGEMENT -----

@app.route('/brands')
def brands():
    """Brand management page."""
    try:
        response = call_api('/api/brands')
        brands_data = response.get('data', [])
        return render_template('brands.html', brands=brands_data)
    except Exception as e:
        logger.error(f"Brands page error: {e}")
        return render_template('brands.html', brands=[])

@app.route('/brands/<int:brand_id>')
def brand_detail(brand_id):
    """Brand detail page."""
    try:
        brand = call_api(f'/api/brands/{brand_id}')
        stats = call_api(f'/api/brands/{brand_id}/stats')
        characters = call_api(f'/api/characters?brand_id={brand_id}')
        videos = call_api(f'/api/videos?brand_id={brand_id}')
        
        return render_template('brand_detail.html',
                             brand=brand.get('data', {}),
                             stats=stats.get('data', {}),
                             characters=characters.get('data', []),
                             videos=videos.get('data', []))
    except Exception as e:
        logger.error(f"Brand detail error: {e}")
        return redirect(url_for('brands'))

# ----- VIDEO MANAGEMENT -----

@app.route('/videos')
def videos():
    """Video library page."""
    try:
        brand_id = request.args.get('brand_id', type=int)
        status = request.args.get('status')
        
        endpoint = '/api/videos?limit=50'
        if brand_id:
            endpoint += f'&brand_id={brand_id}'
        if status:
            endpoint += f'&status={status}'
        
        response = call_api(endpoint)
        videos_data = response.get('data', [])
        
        # Get brands for filter
        brands_response = call_api('/api/brands')
        brands_data = brands_response.get('data', [])
        
        return render_template('videos.html', 
                             videos=videos_data,
                             brands=brands_data,
                             selected_brand=brand_id,
                             selected_status=status)
    except Exception as e:
        logger.error(f"Videos page error: {e}")
        return render_template('videos.html', videos=[], brands=[])

@app.route('/videos/<int:video_id>')
def video_detail(video_id):
    """Video detail page."""
    try:
        video = call_api(f'/api/videos/{video_id}')
        return render_template('video_detail.html', video=video.get('data', {}))
    except Exception as e:
        logger.error(f"Video detail error: {e}")
        return redirect(url_for('videos'))

# ----- CHARACTER MANAGEMENT -----

@app.route('/characters')
def characters():
    """Character management page."""
    try:
        brand_id = request.args.get('brand_id', type=int)
        
        endpoint = '/api/characters'
        if brand_id:
            endpoint += f'?brand_id={brand_id}'
        
        response = call_api(endpoint)
        characters_data = response.get('data', [])
        
        # Get brands for filter
        brands_response = call_api('/api/brands')
        brands_data = brands_response.get('data', [])
        
        return render_template('characters.html',
                             characters=characters_data,
                             brands=brands_data,
                             selected_brand=brand_id)
    except Exception as e:
        logger.error(f"Characters page error: {e}")
        return render_template('characters.html', characters=[], brands=[])

@app.route('/characters/<int:character_id>')
def character_detail(character_id):
    """Character detail page."""
    try:
        character = call_api(f'/api/characters/{character_id}')
        stats = call_api(f'/api/characters/{character_id}/stats')
        
        return render_template('character_detail.html',
                             character=character.get('data', {}),
                             stats=stats.get('data', {}))
    except Exception as e:
        logger.error(f"Character detail error: {e}")
        return redirect(url_for('characters'))

# ----- CONTENT STRATEGY -----

@app.route('/content')
def content_strategy():
    """Content strategy and planning page."""
    try:
        brands_response = call_api('/api/brands?active=true')
        brands_data = brands_response.get('data', [])
        
        return render_template('content.html', brands=brands_data)
    except Exception as e:
        logger.error(f"Content page error: {e}")
        return render_template('content.html', brands=[])

# ----- DEBUG & MONITORING -----

@app.route('/debug')
def debug():
    """Advanced debug and monitoring UI."""
    try:
        # Get system health
        health = call_api('/api/system/health')
        stats = call_api('/api/system/stats')
        config = call_api('/api/system/config')
        
        return render_template('debug.html',
                             health=health.get('data', {}),
                             stats=stats.get('data', {}),
                             config=config.get('data', {}),
                             backend_url=BACKEND_URL)
    except Exception as e:
        logger.error(f"Debug page error: {e}")
        return render_template('debug.html',
                             health={}, stats={}, config={},
                             backend_url=BACKEND_URL)

# ----- API PROXY ENDPOINTS -----

@app.route('/api/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    """Proxy API calls to backend."""
    data = request.get_json() if request.method in ['POST', 'PUT'] else None
    result = call_api(f'/api/{endpoint}', method=request.method, data=data)
    return jsonify(result)

# ----- ERROR HANDLERS -----

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404,
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return render_template('error.html',
                         error_code=500,
                         error_message='Internal server error'), 500

if __name__ == '__main__':
    port = int(os.getenv('FRONTEND_PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting KIVerdienst v2 Frontend on port {port}")
    logger.info(f"Backend API: {BACKEND_URL}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
