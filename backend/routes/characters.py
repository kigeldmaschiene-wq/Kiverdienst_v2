"""
Character management routes
"""
from flask import Blueprint, jsonify, request
from database import get_session
from models import Character, Brand
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('characters', __name__)

@bp.route('', methods=['GET'])
def get_characters():
    """Get all characters with optional brand filter"""
    try:
        db = get_session()
        query = db.query(Character)
        
        # Filter by brand
        brand_id = request.args.get('brand_id', type=int)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        characters = query.order_by(Character.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [character.to_dict() for character in characters]
        })
    except Exception as e:
        logger.error(f"Error fetching characters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:character_id>', methods=['GET'])
def get_character(character_id):
    """Get a specific character"""
    try:
        db = get_session()
        character = db.query(Character).filter_by(id=character_id).first()
        
        if not character:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': character.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching character {character_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('', methods=['POST'])
def create_character():
    """Create a new character"""
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
        
        db = get_session()
        
        # Verify brand exists
        brand = db.query(Brand).filter_by(id=data['brand_id']).first()
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        character = Character(
            brand_id=data['brand_id'],
            name=data['name'],
            gender=data.get('gender', 'neutral'),
            voice_id=data.get('voice_id', ''),
            personality=data.get('personality', '')
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        
        logger.info(f"Created character: {character.name} (ID: {character.id})")
        return jsonify({
            'success': True,
            'data': character.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    """Update a character"""
    try:
        data = request.get_json()
        db = get_session()
        
        character = db.query(Character).filter_by(id=character_id).first()
        if not character:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
        
        # Update fields
        if 'name' in data:
            character.name = data['name']
        if 'gender' in data:
            character.gender = data['gender']
        if 'voice_id' in data:
            character.voice_id = data['voice_id']
        if 'personality' in data:
            character.personality = data['personality']
        
        db.commit()
        db.refresh(character)
        
        logger.info(f"Updated character: {character.name} (ID: {character.id})")
        return jsonify({
            'success': True,
            'data': character.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating character {character_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@bp.route('/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    """Delete a character"""
    try:
        db = get_session()
        character = db.query(Character).filter_by(id=character_id).first()
        
        if not character:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
        
        character_name = character.name
        db.delete(character)
        db.commit()
        
        logger.info(f"Deleted character: {character_name} (ID: {character_id})")
        return jsonify({
            'success': True,
            'message': f'Character "{character_name}" deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting character {character_id}: {e}")
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
