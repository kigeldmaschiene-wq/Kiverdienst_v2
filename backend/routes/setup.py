"""
Setup wizard endpoints.
"""
from flask import Blueprint, jsonify, request
from database import test_connection, init_db, SessionLocal
from models import SystemConfig
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('setup', __name__)

@bp.route('/status', methods=['GET'])
def get_setup_status():
    """Check if setup has been completed."""
    try:
        db = SessionLocal()
        try:
            # Check if setup_completed config exists
            config = db.query(SystemConfig).filter(
                SystemConfig.key == 'setup_completed'
            ).first()
            
            completed = config and config.value == 'true'
            
            return jsonify({
                'success': True,
                'data': {
                    'completed': completed,
                    'database_connected': test_connection()
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error checking setup status: {e}")
        return jsonify({
            'success': True,
            'data': {
                'completed': False,
                'database_connected': False
            }
        })

@bp.route('/init', methods=['POST'])
def initialize_setup():
    """Initialize database and system."""
    try:
        # Test connection
        if not test_connection():
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        # Initialize database tables
        if not init_db():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize database tables'
            }), 500
        
        # Create initial system config
        db = SessionLocal()
        try:
            # Check if configs already exist
            existing = db.query(SystemConfig).count()
            
            if existing == 0:
                # Create default configs
                default_configs = [
                    SystemConfig(
                        key='setup_completed',
                        value='false',
                        description='Whether initial setup is completed'
                    ),
                    SystemConfig(
                        key='system_initialized',
                        value='true',
                        description='System initialization timestamp'
                    ),
                    SystemConfig(
                        key='ollama_url',
                        value='http://ollama:11434',
                        description='Ollama API URL'
                    ),
                    SystemConfig(
                        key='default_model',
                        value='llama2',
                        description='Default LLM model for content generation'
                    )
                ]
                
                for config in default_configs:
                    db.add(config)
                
                db.commit()
                logger.info("Default system configuration created")
            
            return jsonify({
                'success': True,
                'message': 'System initialized successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing setup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/complete', methods=['POST'])
def complete_setup():
    """Mark setup as completed."""
    try:
        data = request.get_json() or {}
        
        db = SessionLocal()
        try:
            # Update or create setup_completed config
            config = db.query(SystemConfig).filter(
                SystemConfig.key == 'setup_completed'
            ).first()
            
            if not config:
                config = SystemConfig(
                    key='setup_completed',
                    description='Whether initial setup is completed'
                )
                db.add(config)
            
            config.value = 'true'
            
            # Store any additional setup data
            if 'ollama_url' in data:
                ollama_config = db.query(SystemConfig).filter(
                    SystemConfig.key == 'ollama_url'
                ).first()
                if ollama_config:
                    ollama_config.value = data['ollama_url']
            
            db.commit()
            logger.info("Setup completed successfully")
            
            return jsonify({
                'success': True,
                'message': 'Setup completed successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error completing setup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/test-database', methods=['GET'])
def test_database():
    """Test database connection."""
    try:
        connected = test_connection()
        
        if connected:
            return jsonify({
                'success': True,
                'message': 'Database connection successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
