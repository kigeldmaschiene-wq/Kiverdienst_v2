"""
KIVerdienst v2 - Backend API
Main Flask application
"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os

# Import database
from database import init_db, test_connection

# Import routes
from routes import setup_bp, brands_bp, videos_bp, characters_bp, system_bp, content_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(setup_bp, url_prefix='/api/setup')
app.register_blueprint(brands_bp, url_prefix='/api/brands')
app.register_blueprint(videos_bp, url_prefix='/api/videos')
app.register_blueprint(characters_bp, url_prefix='/api/characters')
app.register_blueprint(system_bp, url_prefix='/api/system')
app.register_blueprint(content_bp, url_prefix='/api/content')

# Root endpoint
@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'name': 'KIVerdienst v2 API',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'system': '/api/system/stats',
            'setup': '/api/setup',
            'brands': '/api/brands',
            'videos': '/api/videos',
            'characters': '/api/characters',
            'content': '/api/content'
        }
    })

# Health check
@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        db_status = test_connection()
        return jsonify({
            'status': 'healthy' if db_status else 'degraded',
            'database': 'connected' if db_status else 'disconnected',
            'service': 'backend-api'
        }), 200 if db_status else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'code': 500
    }), 500

# Initialize database on startup
@app.before_request
def before_first_request():
    """Initialize database on first request"""
    if not hasattr(app, 'db_initialized'):
        try:
            init_db()
            app.db_initialized = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting KIVerdienst v2 Backend API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
