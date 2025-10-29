#!/usr/bin/env python3
"""
KIVerdienst v2 - Database Initialization Script

This script initializes the database schema and optionally loads sample data.
Usage: python init_db.py [--samples] [--reset]
"""

import os
import sys
import argparse
import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Create database connection from environment variables
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'kiverdienst_v2'),
            user=os.getenv('POSTGRES_USER', 'kiverdienst'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        logger.info("✓ Database connection established")
        return conn
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        sys.exit(1)


def execute_sql_file(conn, filepath):
    """
    Execute SQL commands from a file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        logger.info(f"✓ Executed SQL file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to execute {filepath}: {e}")
        conn.rollback()
        return False


def reset_database(conn):
    """
    Drop all tables (for reset)
    """
    logger.warning("Resetting database - all data will be lost!")
    
    try:
        cursor = conn.cursor()
        
        # Drop all tables in reverse order (respecting foreign keys)
        tables = [
            'performance_analytics',
            'posting_schedule',
            'products',
            'system_logs',
            'videos',
            'video_scripts',
            'characters',
            'brands',
            'system_config'
        ]
        
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            logger.info(f"  Dropped table: {table}")
        
        # Drop views
        cursor.execute("DROP VIEW IF EXISTS brand_performance CASCADE")
        cursor.execute("DROP VIEW IF EXISTS recent_activity CASCADE")
        
        # Drop functions
        cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE")
        
        conn.commit()
        cursor.close()
        
        logger.info("✓ Database reset complete")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to reset database: {e}")
        conn.rollback()
        return False


def check_tables_exist(conn):
    """
    Check if database tables exist
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False


def verify_installation(conn):
    """
    Verify database installation
    """
    logger.info("Verifying installation...")
    
    try:
        cursor = conn.cursor()
        
        # Count tables
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        table_count = cursor.fetchone()[0]
        
        # Count views
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.views 
            WHERE table_schema = 'public'
        """)
        view_count = cursor.fetchone()[0]
        
        # Count system config entries
        cursor.execute("SELECT count(*) FROM system_config")
        config_count = cursor.fetchone()[0]
        
        cursor.close()
        
        logger.info(f"✓ Tables created: {table_count}")
        logger.info(f"✓ Views created: {view_count}")
        logger.info(f"✓ System config entries: {config_count}")
        
        return table_count >= 9 and view_count >= 2 and config_count > 0
    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False


def main():
    """
    Main initialization function
    """
    parser = argparse.ArgumentParser(description='Initialize KIVerdienst v2 database')
    parser.add_argument('--samples', action='store_true', help='Load sample data')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: deletes all data)')
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("KIVerdienst v2 - Database Initialization")
    logger.info("=" * 70)
    
    # Get database connection
    conn = get_db_connection()
    
    try:
        # Reset if requested
        if args.reset:
            if not reset_database(conn):
                logger.error("Failed to reset database")
                sys.exit(1)
        
        # Check if tables already exist
        if check_tables_exist(conn) and not args.reset:
            logger.warning("Tables already exist. Use --reset to recreate them.")
            
            # Verify existing installation
            if verify_installation(conn):
                logger.info("✓ Database is properly initialized")
                return
            else:
                logger.error("✗ Database verification failed")
                sys.exit(1)
        
        # Get SQL file paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_dir = os.path.join(os.path.dirname(script_dir), 'sql')
        schema_file = os.path.join(sql_dir, 'schema.sql')
        seed_file = os.path.join(sql_dir, 'seed.sql')
        
        # Execute schema
        logger.info("Creating database schema...")
        if not execute_sql_file(conn, schema_file):
            logger.error("Failed to create schema")
            sys.exit(1)
        
        # Execute seed data if requested
        if args.samples:
            logger.info("Loading sample data...")
            if os.path.exists(seed_file):
                if not execute_sql_file(conn, seed_file):
                    logger.error("Failed to load sample data")
                    sys.exit(1)
            else:
                logger.warning(f"Seed file not found: {seed_file}")
        
        # Verify installation
        if verify_installation(conn):
            logger.info("")
            logger.info("=" * 70)
            logger.info("✓ Database initialization completed successfully!")
            logger.info("=" * 70)
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Access the web interface at http://YOUR-IP:5000/setup")
            logger.info("  2. Complete the setup wizard")
            logger.info("  3. Start creating content!")
            logger.info("")
        else:
            logger.error("✗ Database verification failed")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}")
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()
