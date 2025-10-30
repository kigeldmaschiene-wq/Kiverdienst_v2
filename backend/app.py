"""
Main Flask application for KIVerdienst v2 Backend API.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Import database
from database import init_db, test_connection, SessionLocal

# Import routes
from routes import setup, brands, videos, characters, system

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
app.register_blueprint(setup.bp, url_prefix='/api/setup')
app.register_blueprint(brands.bp, url_prefix='/api/brands')
app.register_blueprint(videos.bp, url_prefix='/api/videos')
app.register_blueprint(characters.bp, url_prefix='/api/characters')
app.register_blueprint(system.bp, url_prefix='/api')

@app.before_request
def log_request():
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.path}")

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Clean up database sessions."""
    SessionLocal.remove()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        db_connected = test_connection()
        
        health_status = {
            'status': 'healthy' if db_connected else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db_connected else 'disconnected',
            'version': '2.0.0'
        }
        
        return jsonify(health_status), 200 if db_connected else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({
        'name': 'KIVerdienst v2 Backend API',
        'version': '2.0.0',
        'endpoints': {
            'health': '/api/health',
            'setup': '/api/setup/*',
            'brands': '/api/brands/*',
            'videos': '/api/videos/*',
            'characters': '/api/characters/*',
            'system': '/api/system/*'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

def initialize_app():
    """Initialize application on startup."""
    logger.info("Starting KIVerdienst v2 Backend API...")
    
    # Test database connection
    if test_connection():
        logger.info("Database connection successful")
        # Initialize tables
        if init_db():
            logger.info("Database tables initialized")
        else:
            logger.warning("Database table initialization failed")
    else:
        logger.error("Database connection failed")
    
    logger.info("Backend API ready")

if __name__ == '__main__':
    initialize_app()
    
    # Run Flask app
    port = int(os.getenv('BACKEND_PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
