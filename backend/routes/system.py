"""
System status and statistics endpoints.
"""
from flask import Blueprint, jsonify, current_app
from database import get_db_stats, test_connection
from models import Brand, Video, Character, SystemConfig
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('system', __name__)

@bp.route('/system/stats', methods=['GET'])
def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            # Brand statistics
            total_brands = db.query(Brand).count()
            active_brands = db.query(Brand).filter(Brand.active == True).count()
            
            # Video statistics
            total_videos = db.query(Video).count()
            posted_videos = db.query(Video).filter(Video.posted == True).count()
            draft_videos = db.query(Video).filter(Video.status == 'draft').count()
            
            # Videos by status
            videos_by_status = db.query(
                Video.status, func.count(Video.id)
            ).group_by(Video.status).all()
            
            status_counts = {status: count for status, count in videos_by_status}
            
            # Character statistics
            total_characters = db.query(Character).count()
            active_characters = db.query(Character).filter(Character.active == True).count()
            
            # Video engagement totals
            engagement = db.query(
                func.sum(Video.views).label('total_views'),
                func.sum(Video.likes).label('total_likes'),
                func.sum(Video.comments).label('total_comments')
            ).first()
            
            stats = {
                'brands': {
                    'total': total_brands,
                    'active': active_brands,
                    'inactive': total_brands - active_brands
                },
                'videos': {
                    'total': total_videos,
                    'posted': posted_videos,
                    'draft': draft_videos,
                    'by_status': status_counts
                },
                'characters': {
                    'total': total_characters,
                    'active': active_characters
                },
                'engagement': {
                    'total_views': int(engagement.total_views or 0),
                    'total_likes': int(engagement.total_likes or 0),
                    'total_comments': int(engagement.total_comments or 0)
                },
                'database': get_db_stats()
            }
            
            return jsonify({'success': True, 'data': stats})
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/system/health', methods=['GET'])
def system_health():
    """Detailed system health check."""
    try:
        db_healthy = test_connection()
        
        health = {
            'overall': 'healthy' if db_healthy else 'degraded',
            'components': {
                'database': 'up' if db_healthy else 'down',
                'api': 'up'
            },
            'database_stats': get_db_stats() if db_healthy else {}
        }
        
        return jsonify({'success': True, 'data': health})
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/system/config', methods=['GET'])
def get_system_config():
    """Get all system configuration."""
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            configs = db.query(SystemConfig).all()
            config_dict = {c.key: c.value for c in configs}
            
            return jsonify({
                'success': True,
                'data': config_dict,
                'items': [c.to_dict() for c in configs]
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/system/config/<key>', methods=['GET', 'PUT'])
def manage_config_key(key):
    """Get or update a specific configuration key."""
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            if request.method == 'GET':
                config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
                if not config:
                    return jsonify({'success': False, 'error': 'Config key not found'}), 404
                return jsonify({'success': True, 'data': config.to_dict()})
            
            elif request.method == 'PUT':
                from flask import request
                data = request.get_json()
                
                config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
                if not config:
                    config = SystemConfig(key=key)
                    db.add(config)
                
                if 'value' in data:
                    config.value = data['value']
                if 'description' in data:
                    config.description = data['description']
                
                db.commit()
                return jsonify({'success': True, 'data': config.to_dict()})
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error managing config key {key}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
