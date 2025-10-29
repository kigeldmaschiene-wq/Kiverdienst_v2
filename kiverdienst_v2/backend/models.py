"""
SQLAlchemy models for KIVerdienst v2
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DECIMAL, 
    ForeignKey, TIMESTAMP, BigInteger, Time, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base


class SystemConfig(Base):
    """System configuration key-value store"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Brand(Base):
    """Brand/Channel configuration"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    niche = Column(String(255), index=True)
    tonality = Column(String(100))
    target_audience = Column(Text)
    
    # Social media accounts
    tiktok_account = Column(String(255))
    instagram_account = Column(String(255))
    youtube_account = Column(String(255))
    
    # Status
    status = Column(String(50), default='active', index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characters = relationship("Character", back_populates="brand", cascade="all, delete-orphan")
    video_scripts = relationship("VideoScript", back_populates="brand", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="brand", cascade="all, delete-orphan")
    posting_schedules = relationship("PostingSchedule", back_populates="brand", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'paused', 'archived')", name='check_brand_status'),
    )


class Character(Base):
    """Character/Avatar configuration for brands"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Basic info
    gender = Column(String(20))
    name = Column(String(255))
    age = Column(Integer)
    
    # Appearance & personality
    appearance_description = Column(Text)
    personality = Column(Text)
    voice_type = Column(String(100))
    
    # AI generation
    sdxl_prompt = Column(Text)
    reference_images_path = Column(Text)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="characters")


class VideoScript(Base):
    """Video script storage"""
    __tablename__ = "video_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Script content
    script_text = Column(Text, nullable=False)
    hook = Column(Text)
    cta = Column(Text)
    
    # Metadata
    estimated_duration = Column(Integer)
    status = Column(String(50), default='draft', index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="video_scripts")
    videos = relationship("Video", back_populates="script")
    
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'approved', 'rejected', 'used')", name='check_script_status'),
    )


class Video(Base):
    """Generated video storage"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE'), nullable=False, index=True)
    script_id = Column(Integer, ForeignKey('video_scripts.id', ondelete='SET NULL'), index=True)
    
    # File paths
    video_path = Column(Text)
    thumbnail_path = Column(Text)
    
    # Video info
    duration = Column(Integer)
    resolution = Column(String(20))
    file_size = Column(BigInteger)
    
    # Quality & status
    quality_score = Column(DECIMAL(3, 2))
    status = Column(String(50), default='processing', index=True)
    
    # Posting info
    posted_at = Column(TIMESTAMP, index=True)
    platform = Column(String(50), index=True)
    post_id = Column(String(255))
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="videos")
    script = relationship("VideoScript", back_populates="videos")
    analytics = relationship("PerformanceAnalytics", back_populates="video", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('processing', 'ready', 'posted', 'failed', 'archived')", name='check_video_status'),
    )


class PerformanceAnalytics(Base):
    """Performance metrics for videos"""
    __tablename__ = "performance_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    
    # Metrics
    views = Column(Integer, default=0, index=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Engagement
    watch_time_avg = Column(Integer)
    completion_rate = Column(DECIMAL(5, 2))
    engagement_rate = Column(DECIMAL(5, 2))
    
    # Additional data
    raw_data = Column(JSONB)
    
    # Timestamps
    collected_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="analytics")


class PostingSchedule(Base):
    """Posting schedule configuration"""
    __tablename__ = "posting_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Schedule info
    platform = Column(String(50), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6, Monday=0
    time_slot = Column(Time, nullable=False)
    
    # Status
    active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="posting_schedules")
    
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name='check_day_of_week'),
    )


class SystemLog(Base):
    """System logs for monitoring and debugging"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Log info
    level = Column(String(20), nullable=False, index=True)
    component = Column(String(100), index=True)
    message = Column(Text, nullable=False)
    
    # Additional data
    details = Column(JSONB)
    
    # Context
    user_id = Column(Integer)
    brand_id = Column(Integer, index=True)
    video_id = Column(Integer)
    
    # Timestamp
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        CheckConstraint("level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name='check_log_level'),
    )


class Product(Base):
    """Product information for affiliate marketing"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Product info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    currency = Column(String(10), default='EUR')
    
    # Affiliate links
    affiliate_link = Column(Text)
    amazon_asin = Column(String(50))
    
    # Media
    image_url = Column(Text)
    
    # Status
    status = Column(String(50), default='active', index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="products")
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name='check_product_status'),
    )
