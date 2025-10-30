"""
Brand management routes
"""
from flask import Blueprint, jsonify, request
from database import get_session
from models import Brand
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('brands', __name__)

@bp.route('', methods=['GET'])
def get_brands():
    """Get all brands"""
    try:
        db = get_session()
        brands = db.query(Brand).order_by(Brand.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [brand.to_dict() for brand in brands]
        })
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get a specific brand"""
    try:
        db = get_session()
        brand = db.query(Brand).filter_by(id=brand_id).first()
        
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': brand.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching brand {brand_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('', methods=['POST'])
def create_brand():
    """Create a new brand"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Brand name is required'
            }), 400
        
        db = get_session()
        
        brand = Brand(
            name=data['name'],
            niche=data.get('niche', ''),
            target_audience=data.get('target_audience', ''),
            content_strategy=data.get('content_strategy', ''),
            active=data.get('active', True)
        )
        
        db.add(brand)
        db.commit()
        db.refresh(brand)
        
        logger.info(f"Created brand: {brand.name} (ID: {brand.id})")
        return jsonify({
            'success': True,
            'data': brand.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update a brand"""
    try:
        data = request.get_json()
        db = get_session()
        
        brand = db.query(Brand).filter_by(id=brand_id).first()
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
        if 'active' in data:
            brand.active = data['active']
        
        db.commit()
        db.refresh(brand)
        
        logger.info(f"Updated brand: {brand.name} (ID: {brand.id})")
        return jsonify({
            'success': True,
            'data': brand.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating brand {brand_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete a brand"""
    try:
        db = get_session()
        brand = db.query(Brand).filter_by(id=brand_id).first()
        
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        brand_name = brand.name
        db.delete(brand)
        db.commit()
        
        logger.info(f"Deleted brand: {brand_name} (ID: {brand_id})")
        return jsonify({
            'success': True,
            'message': f'Brand "{brand_name}" deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting brand {brand_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:brand_id>/stats', methods=['GET'])
def get_brand_stats(brand_id):
    """Get statistics for a brand"""
    try:
        db = get_session()
        brand = db.query(Brand).filter_by(id=brand_id).first()
        
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        stats = {
            'brand': brand.to_dict(),
            'characters': len(brand.characters),
            'total_videos': len(brand.videos),
            'posted_videos': sum(1 for v in brand.videos if v.posted),
            'draft_videos': sum(1 for v in brand.videos if v.status == 'draft'),
            'total_views': sum(v.views for v in brand.videos if v.views),
            'total_likes': sum(v.likes for v in brand.videos if v.likes)
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error fetching brand stats {brand_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
