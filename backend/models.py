"""
Database models for KIVerdienst v2
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class SystemConfig(Base):
    """System configuration key-value store"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Brand(Base):
    """Content brand/channel"""
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    niche = Column(String(100))
    target_audience = Column(Text)
    content_strategy = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    characters = relationship('Character', back_populates='brand', cascade='all, delete-orphan')
    videos = relationship('Video', back_populates='brand', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'niche': self.niche,
            'target_audience': self.target_audience,
            'content_strategy': self.content_strategy,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'character_count': len(self.characters) if self.characters else 0,
            'video_count': len(self.videos) if self.videos else 0
        }

class Character(Base):
    """AI character for content creation"""
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    name = Column(String(100), nullable=False)
    gender = Column(String(20))
    voice_id = Column(String(100))
    personality = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brand = relationship('Brand', back_populates='characters')
    videos = relationship('Video', back_populates='character')
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'brand_name': self.brand.name if self.brand else None,
            'name': self.name,
            'gender': self.gender,
            'voice_id': self.voice_id,
            'personality': self.personality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'video_count': len(self.videos) if self.videos else 0
        }

class Video(Base):
    """Generated video content"""
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'))
    title = Column(String(200), nullable=False)
    script = Column(Text)
    status = Column(String(50), default='draft')
    posted = Column(Boolean, default=False)
    platform = Column(String(50))
    video_path = Column(String(500))
    thumbnail_path = Column(String(500))
    duration = Column(Integer)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    posted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brand = relationship('Brand', back_populates='videos')
    character = relationship('Character', back_populates='videos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'brand_name': self.brand.name if self.brand else None,
            'character_id': self.character_id,
            'character_name': self.character.name if self.character else None,
            'title': self.title,
            'script': self.script,
            'status': self.status,
            'posted': self.posted,
            'platform': self.platform,
            'video_path': self.video_path,
            'thumbnail_path': self.thumbnail_path,
            'duration': self.duration,
            'views': self.views,
            'likes': self.likes,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContentIdea(Base):
    """AI-generated content ideas"""
    __tablename__ = 'content_ideas'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    trending_score = Column(Integer, default=0)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'trending_score': self.trending_score,
            'used': self.used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
