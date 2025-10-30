"""
Video management routes
"""
from flask import Blueprint, jsonify, request
from database import get_session
from models import Video, Brand, Character
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('videos', __name__)

@bp.route('', methods=['GET'])
def get_videos():
    """Get all videos with optional filters"""
    try:
        db = get_session()
        query = db.query(Video)
        
        # Filter by brand
        brand_id = request.args.get('brand_id', type=int)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        # Filter by posted
        posted = request.args.get('posted')
        if posted is not None:
            query = query.filter_by(posted=posted.lower() == 'true')
        
        videos = query.order_by(Video.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [video.to_dict() for video in videos]
        })
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get a specific video"""
    try:
        db = get_session()
        video = db.query(Video).filter_by(id=video_id).first()
        
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': video.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching video {video_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('', methods=['POST'])
def create_video():
    """Create a new video"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('brand_id'):
            return jsonify({
                'success': False,
                'error': 'Brand ID is required'
            }), 400
        
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        db = get_session()
        
        # Verify brand exists
        brand = db.query(Brand).filter_by(id=data['brand_id']).first()
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        # Verify character exists (if provided)
        if data.get('character_id'):
            character = db.query(Character).filter_by(id=data['character_id']).first()
            if not character:
                return jsonify({
                    'success': False,
                    'error': 'Character not found'
                }), 404
        
        video = Video(
            brand_id=data['brand_id'],
            character_id=data.get('character_id'),
            title=data['title'],
            script=data.get('script', ''),
            status=data.get('status', 'draft'),
            platform=data.get('platform', 'tiktok')
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Created video: {video.title} (ID: {video.id})")
        return jsonify({
            'success': True,
            'data': video.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:video_id>', methods=['PUT'])
def update_video(video_id):
    """Update a video"""
    try:
        data = request.get_json()
        db = get_session()
        
        video = db.query(Video).filter_by(id=video_id).first()
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        # Update fields
        updatable_fields = ['title', 'script', 'status', 'posted', 'platform', 
                           'video_path', 'thumbnail_path', 'duration', 'views', 'likes']
        
        for field in updatable_fields:
            if field in data:
                setattr(video, field, data[field])
        
        db.commit()
        db.refresh(video)
        
        logger.info(f"Updated video: {video.title} (ID: {video.id})")
        return jsonify({
            'success': True,
            'data': video.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating video {video_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video"""
    try:
        db = get_session()
        video = db.query(Video).filter_by(id=video_id).first()
        
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        video_title = video.title
        db.delete(video)
        db.commit()
        
        logger.info(f"Deleted video: {video_title} (ID: {video_id})")
        return jsonify({
            'success': True,
            'message': f'Video "{video_title}" deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
