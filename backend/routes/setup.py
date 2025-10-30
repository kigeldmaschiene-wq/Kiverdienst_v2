"""
Setup wizard routes
"""
from flask import Blueprint, jsonify, request
from database import get_session, init_db
from models import SystemConfig
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('setup', __name__)

@bp.route('/status', methods=['GET'])
def get_setup_status():
    """Check if setup is completed"""
    try:
        db = get_session()
        config = db.query(SystemConfig).filter_by(key='setup_completed').first()
        
        completed = config.value == 'true' if config else False
        
        return jsonify({
            'success': True,
            'data': {
                'completed': completed,
                'step': config.value if config and not completed else None
            }
        })
    except Exception as e:
        logger.error(f"Error checking setup status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/init', methods=['POST'])
def initialize_setup():
    """Initialize system setup"""
    try:
        # Initialize database
        if not init_db():
            raise Exception("Failed to initialize database")
        
        db = get_session()
        
        # Create default system configs
        configs = [
            SystemConfig(
                key='setup_completed',
                value='false',
                description='Setup wizard completion status'
            ),
            SystemConfig(
                key='system_name',
                value='KIVerdienst v2',
                description='System name'
            ),
            SystemConfig(
                key='version',
                value='2.0.0',
                description='System version'
            )
        ]
        
        for config in configs:
            existing = db.query(SystemConfig).filter_by(key=config.key).first()
            if not existing:
                db.add(config)
        
        db.commit()
        
        logger.info("System initialized successfully")
        return jsonify({
            'success': True,
            'message': 'System initialized successfully'
        })
    except Exception as e:
        logger.error(f"Error initializing setup: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/complete', methods=['POST'])
def complete_setup():
    """Mark setup as completed"""
    try:
        db = get_session()
        
        config = db.query(SystemConfig).filter_by(key='setup_completed').first()
        if config:
            config.value = 'true'
        else:
            config = SystemConfig(
                key='setup_completed',
                value='true',
                description='Setup wizard completion status'
            )
            db.add(config)
        
        db.commit()
        
        logger.info("Setup completed successfully")
        return jsonify({
            'success': True,
            'message': 'Setup completed successfully'
        })
    except Exception as e:
        logger.error(f"Error completing setup: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update system configuration"""
    try:
        db = get_session()
        
        if request.method == 'GET':
            configs = db.query(SystemConfig).all()
            return jsonify({
                'success': True,
                'data': [config.to_dict() for config in configs]
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            key = data.get('key')
            value = data.get('value')
            description = data.get('description', '')
            
            if not key:
                return jsonify({
                    'success': False,
                    'error': 'Key is required'
                }), 400
            
            config = db.query(SystemConfig).filter_by(key=key).first()
            if config:
                config.value = value
                config.description = description
            else:
                config = SystemConfig(
                    key=key,
                    value=value,
                    description=description
                )
                db.add(config)
            
            db.commit()
            
            return jsonify({
                'success': True,
                'data': config.to_dict()
            })
    except Exception as e:
        logger.error(f"Error managing config: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
