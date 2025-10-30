#!/usr/bin/env python3
"""
Database initialization script for KIVerdienst v2.
Run this to create initial database schema and seed data.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, Base, SessionLocal, test_connection
from models import SystemConfig, Brand, Character, Video
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database schema."""
    logger.info("Initializing database...")
    
    # Test connection
    if not test_connection():
        logger.error("Database connection failed!")
        return False
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def seed_data():
    """Seed initial data."""
    logger.info("Seeding initial data...")
    
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(SystemConfig).count()
        if existing > 0:
            logger.info("Database already seeded, skipping...")
            return True
        
        # Create system config
        configs = [
            SystemConfig(
                key='setup_completed',
                value='false',
                description='Whether initial setup is completed'
            ),
            SystemConfig(
                key='system_version',
                value='2.0.0',
                description='System version'
            ),
            SystemConfig(
                key='ollama_url',
                value='http://ollama:11434',
                description='Ollama API URL for LLM'
            ),
            SystemConfig(
                key='default_model',
                value='llama2',
                description='Default LLM model'
            )
        ]
        
        for config in configs:
            db.add(config)
        
        db.commit()
        logger.info("System configuration seeded")
        
        # Optionally create demo brand
        demo_mode = os.getenv('SEED_DEMO_DATA', 'false').lower() == 'true'
        
        if demo_mode:
            logger.info("Creating demo data...")
            
            demo_brand = Brand(
                name='Demo Brand',
                niche='Technology',
                target_audience='Tech enthusiasts aged 18-35',
                content_strategy='Educational and entertaining content about latest tech trends',
                platforms=['tiktok', 'instagram'],
                active=True
            )
            db.add(demo_brand)
            db.commit()
            db.refresh(demo_brand)
            
            # Create demo character
            demo_character = Character(
                brand_id=demo_brand.id,
                name='Alex',
                gender='neutral',
                personality='Enthusiastic, knowledgeable, and friendly tech expert',
                speaking_style='Clear, energetic, uses analogies to explain complex topics',
                active=True
            )
            db.add(demo_character)
            db.commit()
            
            logger.info("Demo data created")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main execution."""
    logger.info("=" * 60)
    logger.info("KIVerdienst v2 - Database Initialization")
    logger.info("=" * 60)
    
    # Initialize database
    if not init_database():
        logger.error("Database initialization failed!")
        sys.exit(1)
    
    # Seed data
    if not seed_data():
        logger.error("Data seeding failed!")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Database initialization completed successfully!")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
