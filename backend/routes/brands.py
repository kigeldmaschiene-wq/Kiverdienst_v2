"""
Brand management endpoints.
"""
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import Brand
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('brands', __name__)

@bp.route('/', methods=['GET'])
def get_brands():
    """Get all brands."""
    try:
        db = SessionLocal()
        try:
            # Optional filtering
            active_only = request.args.get('active', 'false').lower() == 'true'
            
            query = db.query(Brand)
            if active_only:
                query = query.filter(Brand.active == True)
            
            brands = query.order_by(Brand.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'data': [brand.to_dict() for brand in brands],
                'total': len(brands)
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get a specific brand by ID."""
    try:
        db = SessionLocal()
        try:
            brand = db.query(Brand).filter(Brand.id == brand_id).first()
            
            if not brand:
                return jsonify({
                    'success': False,
                    'error': 'Brand not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': brand.to_dict()
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting brand {brand_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_brand():
    """Create a new brand."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Brand name is required'
            }), 400
        
        db = SessionLocal()
        try:
            # Create new brand
            brand = Brand(
                name=data['name'],
                niche=data.get('niche'),
                target_audience=data.get('target_audience'),
                content_strategy=data.get('content_strategy'),
                platforms=data.get('platforms', []),
                posting_schedule=data.get('posting_schedule', {}),
                active=data.get('active', True)
            )
            
            db.add(brand)
            db.commit()
            db.refresh(brand)
            
            logger.info(f"Brand created: {brand.name} (ID: {brand.id})")
            
            return jsonify({
                'success': True,
                'data': brand.to_dict(),
                'message': 'Brand created successfully'
            }), 201
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update an existing brand."""
    try:
        data = request.get_json()
        
        db = SessionLocal()
        try:
            brand = db.query(Brand).filter(Brand.id == brand_id).first()
            
            if not brand:
                return jsonify({
                    'success': False,
                    'error': 'Brand not found'
                }), 404
            
            # Update fields
            if 'name' in data:
                brand.name = data['name']
            if 'niche' in data:
                brand.niche = data['niche']
            if 'target_audience' in data:
                brand.target_audience = data['target_audience']
            if 'content_strategy' in data:
                brand.content_strategy = data['content_strategy']
            if 'platforms' in data:
                brand.platforms = data['platforms']
            if 'posting_schedule' in data:
                brand.posting_schedule = data['posting_schedule']
            if 'active' in data:
                brand.active = data['active']
            
            db.commit()
            db.refresh(brand)
            
            logger.info(f"Brand updated: {brand.name} (ID: {brand.id})")
            
            return jsonify({
                'success': True,
                'data': brand.to_dict(),
                'message': 'Brand updated successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating brand {brand_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete a brand."""
    try:
        db = SessionLocal()
        try:
            brand = db.query(Brand).filter(Brand.id == brand_id).first()
            
            if not brand:
                return jsonify({
                    'success': False,
                    'error': 'Brand not found'
                }), 404
            
            brand_name = brand.name
            db.delete(brand)
            db.commit()
            
            logger.info(f"Brand deleted: {brand_name} (ID: {brand_id})")
            
            return jsonify({
                'success': True,
                'message': f'Brand "{brand_name}" deleted successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error deleting brand {brand_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:brand_id>/stats', methods=['GET'])
def get_brand_stats(brand_id):
    """Get statistics for a specific brand."""
    try:
        db = SessionLocal()
        try:
            from models import Video, Character
            from sqlalchemy import func
            
            brand = db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return jsonify({
                    'success': False,
                    'error': 'Brand not found'
                }), 404
            
            # Video stats
            video_count = db.query(Video).filter(Video.brand_id == brand_id).count()
            posted_count = db.query(Video).filter(
                Video.brand_id == brand_id,
                Video.posted == True
            ).count()
            
            # Engagement stats
            engagement = db.query(
                func.sum(Video.views).label('total_views'),
                func.sum(Video.likes).label('total_likes'),
                func.sum(Video.comments).label('total_comments')
            ).filter(Video.brand_id == brand_id).first()
            
            # Character count
            character_count = db.query(Character).filter(
                Character.brand_id == brand_id
            ).count()
            
            stats = {
                'brand': brand.to_dict(),
                'videos': {
                    'total': video_count,
                    'posted': posted_count,
                    'draft': video_count - posted_count
                },
                'characters': character_count,
                'engagement': {
                    'views': int(engagement.total_views or 0),
                    'likes': int(engagement.total_likes or 0),
                    'comments': int(engagement.total_comments or 0)
                }
            }
            
            return jsonify({'success': True, 'data': stats})
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting brand stats for {brand_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
