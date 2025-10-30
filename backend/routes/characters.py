"""
Character management endpoints.
"""
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import Character, Brand
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('characters', __name__)

@bp.route('/', methods=['GET'])
def get_characters():
    """Get all characters with optional filtering."""
    try:
        db = SessionLocal()
        try:
            # Optional filters
            brand_id = request.args.get('brand_id', type=int)
            active_only = request.args.get('active', 'false').lower() == 'true'
            
            query = db.query(Character)
            
            if brand_id:
                query = query.filter(Character.brand_id == brand_id)
            if active_only:
                query = query.filter(Character.active == True)
            
            characters = query.order_by(Character.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'data': [char.to_dict() for char in characters],
                'total': len(characters)
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting characters: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:character_id>', methods=['GET'])
def get_character(character_id):
    """Get a specific character by ID."""
    try:
        db = SessionLocal()
        try:
            character = db.query(Character).filter(Character.id == character_id).first()
            
            if not character:
                return jsonify({
                    'success': False,
                    'error': 'Character not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': character.to_dict()
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting character {character_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_character():
    """Create a new character."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('brand_id'):
            return jsonify({
                'success': False,
                'error': 'Brand ID is required'
            }), 400
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Character name is required'
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
            
            # Create new character
            character = Character(
                brand_id=data['brand_id'],
                name=data['name'],
                gender=data.get('gender'),
                voice_id=data.get('voice_id'),
                personality=data.get('personality'),
                speaking_style=data.get('speaking_style'),
                active=data.get('active', True)
            )
            
            db.add(character)
            db.commit()
            db.refresh(character)
            
            logger.info(f"Character created: {character.name} (ID: {character.id})")
            
            return jsonify({
                'success': True,
                'data': character.to_dict(),
                'message': 'Character created successfully'
            }), 201
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    """Update an existing character."""
    try:
        data = request.get_json()
        
        db = SessionLocal()
        try:
            character = db.query(Character).filter(Character.id == character_id).first()
            
            if not character:
                return jsonify({
                    'success': False,
                    'error': 'Character not found'
                }), 404
            
            # Update fields
            updatable_fields = [
                'name', 'gender', 'voice_id', 'personality',
                'speaking_style', 'active'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(character, field, data[field])
            
            db.commit()
            db.refresh(character)
            
            logger.info(f"Character updated: {character.name} (ID: {character.id})")
            
            return jsonify({
                'success': True,
                'data': character.to_dict(),
                'message': 'Character updated successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating character {character_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    """Delete a character."""
    try:
        db = SessionLocal()
        try:
            character = db.query(Character).filter(Character.id == character_id).first()
            
            if not character:
                return jsonify({
                    'success': False,
                    'error': 'Character not found'
                }), 404
            
            character_name = character.name
            db.delete(character)
            db.commit()
            
            logger.info(f"Character deleted: {character_name} (ID: {character_id})")
            
            return jsonify({
                'success': True,
                'message': f'Character "{character_name}" deleted successfully'
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error deleting character {character_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:character_id>/stats', methods=['GET'])
def get_character_stats(character_id):
    """Get statistics for a specific character."""
    try:
        db = SessionLocal()
        try:
            from models import Video
            from sqlalchemy import func
            
            character = db.query(Character).filter(Character.id == character_id).first()
            if not character:
                return jsonify({
                    'success': False,
                    'error': 'Character not found'
                }), 404
            
            # Video count
            video_count = db.query(Video).filter(Video.character_id == character_id).count()
            
            # Engagement stats
            engagement = db.query(
                func.sum(Video.views).label('total_views'),
                func.sum(Video.likes).label('total_likes'),
                func.sum(Video.comments).label('total_comments')
            ).filter(Video.character_id == character_id).first()
            
            stats = {
                'character': character.to_dict(),
                'videos': {
                    'total': video_count
                },
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
        logger.error(f"Error getting character stats for {character_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
