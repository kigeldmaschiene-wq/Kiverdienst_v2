"""
Database configuration and connection management for KIVerdienst v2.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 
    'postgresql://kiverdienst:secure123kiverdienst@postgres:5432/kiverdienst_v2')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
)

# Session factory
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))

# Base class for models
Base = declarative_base()

def get_db():
    """Get database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_db_stats():
    """Get database statistics."""
    try:
        with engine.connect() as conn:
            # Get table counts
            tables = ['brands', 'characters', 'videos', 'system_config']
            stats = {}
            
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    stats[table] = count
                except Exception as e:
                    logger.warning(f"Could not get count for {table}: {e}")
                    stats[table] = 0
            
            # Get database size
            result = conn.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            ))
            stats['database_size'] = result.fetchone()[0]
            
            return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}
