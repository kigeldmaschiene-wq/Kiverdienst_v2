"""
Database connection and session management for KIVerdienst v2
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kiverdienst:password@postgres:5432/kiverdienst_v2"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", 20)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 10)),
    pool_pre_ping=True,  # Verify connections before using them
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    This should be called when the application starts
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection():
    """
    Check if database connection is working
    Returns: tuple (success: bool, message: str)
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"
