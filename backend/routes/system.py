"""
System statistics and monitoring routes
"""
from flask import Blueprint, jsonify
from database import get_session, test_connection
from models import Brand, Video, Character, SystemConfig
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('system', __name__)

@bp.route('/stats', methods=['GET'])
def get_system_stats():
    """Get overall system statistics"""
    try:
        db = get_session()
        
        # Count totals
        total_brands = db.query(Brand).count()
        active_brands = db.query(Brand).filter_by(active=True).count()
        total_characters = db.query(Character).count()
        total_videos = db.query(Video).count()
        posted_videos = db.query(Video).filter_by(posted=True).count()
        draft_videos = db.query(Video).filter_by(status='draft').count()
        
        # Calculate views and likes
        total_views = db.query(func.sum(Video.views)).scalar() or 0
        total_likes = db.query(func.sum(Video.likes)).scalar() or 0
        
        # Get recent activity
        recent_videos = db.query(Video)\
            .order_by(Video.created_at.desc())\
            .limit(5)\
            .all()
        
        stats = {
            'brands': {
                'total': total_brands,
                'active': active_brands,
                'inactive': total_brands - active_brands
            },
            'characters': {
                'total': total_characters
            },
            'videos': {
                'total': total_videos,
                'posted': posted_videos,
                'draft': draft_videos,
                'pending': total_videos - posted_videos - draft_videos
            },
            'engagement': {
                'total_views': int(total_views),
                'total_likes': int(total_likes),
                'avg_views': int(total_views / posted_videos) if posted_videos > 0 else 0,
                'avg_likes': int(total_likes / posted_videos) if posted_videos > 0 else 0
            },
            'recent_videos': [video.to_dict() for video in recent_videos]
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/health', methods=['GET'])
def system_health():
    """Comprehensive system health check"""
    try:
        health_status = {
            'status': 'healthy',
            'components': {}
        }
        
        # Check database
        db_healthy = test_connection()
        health_status['components']['database'] = {
            'status': 'up' if db_healthy else 'down',
            'type': 'postgresql'
        }
        
        # Check if we can query
        try:
            db = get_session()
            db.query(SystemConfig).first()
            health_status['components']['database']['accessible'] = True
        except Exception as e:
            health_status['components']['database']['accessible'] = False
            health_status['components']['database']['error'] = str(e)
            health_status['status'] = 'degraded'
        finally:
            db.close()
        
        # Overall status
        if not db_healthy:
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify({
            'success': True,
            'data': health_status
        }), status_code
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'unhealthy'
        }), 503

@bp.route('/config', methods=['GET'])
def get_system_config():
    """Get all system configuration"""
    try:
        db = get_session()
        configs = db.query(SystemConfig).all()
        
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        })
    except Exception as e:
        logger.error(f"Error fetching system config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        import platform
        import sys
        
        info = {
            'name': 'KIVerdienst v2',
            'version': '2.0.0',
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.machine()
        }
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"Error fetching system info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
