"""
Content generation and strategy routes
"""
from flask import Blueprint, jsonify, request
from database import get_session
from models import ContentIdea, Brand
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('content', __name__)

@bp.route('/ideas', methods=['GET'])
def get_content_ideas():
    """Get content ideas with optional brand filter"""
    try:
        db = get_session()
        query = db.query(ContentIdea)
        
        # Filter by brand
        brand_id = request.args.get('brand_id', type=int)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        # Filter by used status
        used = request.args.get('used')
        if used is not None:
            query = query.filter_by(used=used.lower() == 'true')
        
        ideas = query.order_by(ContentIdea.trending_score.desc(), 
                              ContentIdea.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [idea.to_dict() for idea in ideas]
        })
    except Exception as e:
        logger.error(f"Error fetching content ideas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/ideas', methods=['POST'])
def create_content_idea():
    """Create a new content idea"""
    try:
        data = request.get_json()
        
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
        
        idea = ContentIdea(
            brand_id=data['brand_id'],
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            trending_score=data.get('trending_score', 0)
        )
        
        db.add(idea)
        db.commit()
        db.refresh(idea)
        
        logger.info(f"Created content idea: {idea.title} (ID: {idea.id})")
        return jsonify({
            'success': True,
            'data': idea.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating content idea: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_content_idea(idea_id):
    """Update a content idea"""
    try:
        data = request.get_json()
        db = get_session()
        
        idea = db.query(ContentIdea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({
                'success': False,
                'error': 'Content idea not found'
            }), 404
        
        # Update fields
        updatable_fields = ['title', 'description', 'category', 'trending_score', 'used']
        for field in updatable_fields:
            if field in data:
                setattr(idea, field, data[field])
        
        db.commit()
        db.refresh(idea)
        
        return jsonify({
            'success': True,
            'data': idea.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating content idea {idea_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/generate', methods=['POST'])
def generate_content():
    """Generate content ideas using AI (placeholder for future implementation)"""
    try:
        data = request.get_json()
        brand_id = data.get('brand_id')
        count = data.get('count', 5)
        
        if not brand_id:
            return jsonify({
                'success': False,
                'error': 'Brand ID is required'
            }), 400
        
        db = get_session()
        brand = db.query(Brand).filter_by(id=brand_id).first()
        
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        # Placeholder: In production, this would call AI agents
        logger.info(f"Content generation requested for brand {brand.name}")
        
        return jsonify({
            'success': True,
            'message': 'Content generation queued',
            'data': {
                'brand_id': brand_id,
                'count': count,
                'status': 'queued'
            }
        })
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
