"""
Video management endpoints.
"""
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import Video, Brand, Character
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('videos', __name__)

@bp.route('/', methods=['GET'])
def get_videos():
    """Get all videos with optional filtering."""
    try:
        db = SessionLocal()
        try:
            # Optional filters
            brand_id = request.args.get('brand_id', type=int)
            status = request.args.get('status')
            posted = request.args.get('posted')
            platform = request.args.get('platform')
            limit = request.args.get('limit', type=int, default=100)
            offset = request.args.get('offset', type=int, default=0)
            
            query = db.query(Video)
            
            # Apply filters
            if brand_id:
                query = query.filter(Video.brand_id == brand_id)
            if status:
                query = query.filter(Video.status == status)
            if posted is not None:
                query = query.filter(Video.posted == (posted.lower() == 'true'))
            if platform:
                query = query.filter(Video.platform == platform)
            
            # Get total count before pagination
            total = query.count()
            
            # Apply pagination
            videos = query.order_by(Video.created_at.desc()).limit(limit).offset(offset).all()
            
            return jsonify({
                'success': True,
                'data': [video.to_dict() for video in videos],
                'total': total,
                'limit': limit,
                'offset': offset
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting videos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get a specific video by ID."""
    try:
        db = SessionLocal()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            
            if not video:
                return jsonify({
                    'success': False,
                    'error': 'Video not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': video.to_dict()
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting video {video_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_video():
    """Create a new video."""
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
        
        db = SessionLocal()
        try:
            # Verify brand exists
            brand = db.query(Brand).filter(Brand.id == data['brand_id']).first()
            if not brand:
                return jsonify({
                    'success': False,
                    'error': 'Brand not found'
                }), 404
            
            # Verify character if provided
            if data.get('character_id'):
                character = db.query(Character).filter(
                    Character.id == data['character_id']
                ).first()
                if not character:
                    return jsonify({
                        'success': False,
                        'error': 'Character not found'
                    }), 404
            
            # Create new video
            video = Video(
                brand_id=data['brand_id'],
                character_id=data.get('character_id'),
                title=data['title'],
                script=data.get('script'),
                hook=data.get('hook'),
                content_type=data.get('content_type'),
                status=data.get('status', 'draft'),
                platform=data.get('platform'),
                metadata=data.get('metadata', {})
            )
            
            db.add(video)
            db.commit()
            db.refresh(video)
            
            logger.info(f"Video created: {video.title} (ID: {video.id})")
            
            return jsonify({
                'success': True,
                'data': video.to_dict(),
                'message': 'Video created successfully'
            }), 201
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:video_id>', methods=['PUT'])
def update_video(video_id):
    """Update an existing video."""
    try:
        data = request.get_json()
        
        db = SessionLocal()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            
            if not video:
                return jsonify({
                    'success': False,
                    'error': 'Video not found'
                }), 404
            
            # Update fields
            updatable_fields = [
                'title', 'script', 'hook', 'content_type', 'status',
                'platform', 'video_path', 'thumbnail_path', 'duration',
                'posted', 'posted_at', 'views', 'likes', 'comments',
                'character_id', 'metadata'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(video, field, data[field])
            
            db.commit()
            db.refresh(video)
            
            logger.info(f"Video updated: {video.title} (ID: {video.id})")
            
            return jsonify({
                'success': True,
                'data': video.to_dict(),
                'message': 'Video updated successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating video {video_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video."""
    try:
        db = SessionLocal()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            
            if not video:
                return jsonify({
                    'success': False,
                    'error': 'Video not found'
                }), 404
            
            video_title = video.title
            db.delete(video)
            db.commit()
            
            logger.info(f"Video deleted: {video_title} (ID: {video_id})")
            
            return jsonify({
                'success': True,
                'message': f'Video "{video_title}" deleted successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk-create', methods=['POST'])
def bulk_create_videos():
    """Create multiple videos at once."""
    try:
        data = request.get_json()
        videos_data = data.get('videos', [])
        
        if not videos_data:
            return jsonify({
                'success': False,
                'error': 'No videos provided'
            }), 400
        
        db = SessionLocal()
        try:
            created_videos = []
            errors = []
            
            for idx, video_data in enumerate(videos_data):
                try:
                    video = Video(
                        brand_id=video_data['brand_id'],
                        character_id=video_data.get('character_id'),
                        title=video_data['title'],
                        script=video_data.get('script'),
                        hook=video_data.get('hook'),
                        content_type=video_data.get('content_type'),
                        status=video_data.get('status', 'draft'),
                        platform=video_data.get('platform'),
                        metadata=video_data.get('metadata', {})
                    )
                    db.add(video)
                    created_videos.append(video)
                except Exception as e:
                    errors.append(f"Video {idx}: {str(e)}")
            
            db.commit()
            
            for video in created_videos:
                db.refresh(video)
            
            logger.info(f"Bulk created {len(created_videos)} videos")
            
            return jsonify({
                'success': True,
                'data': [v.to_dict() for v in created_videos],
                'created': len(created_videos),
                'errors': errors
            }), 201
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error bulk creating videos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
