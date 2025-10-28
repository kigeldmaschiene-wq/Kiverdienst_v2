#!/usr/bin/env python3
"""
KIVerdienst v2 Database Initialization Script

This script initializes the PostgreSQL database by:
1. Connecting to PostgreSQL using environment variables
2. Checking if tables already exist
3. Running the schema.sql file if needed
4. Verifying the database setup
5. Providing detailed logging and error handling
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("ERROR: psycopg2 not installed. Install it with: pip install psycopg2-binary")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/kiverdienst_init.log')
    ]
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles database initialization and setup"""
    
    def __init__(self):
        """Initialize with environment variables"""
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'kiverdienst_v2'),
            'user': os.getenv('POSTGRES_USER', 'kiverdienst'),
            'password': os.getenv('POSTGRES_PASSWORD')
        }
        
        # Validate required environment variables
        if not self.db_config['password']:
            raise ValueError("POSTGRES_PASSWORD environment variable is required")
        
        self.schema_file = Path('/opt/kiverdienst_v2/sql/schema.sql')
        self.connection: Optional[psycopg2.extensions.connection] = None
        
    def wait_for_database(self, max_retries: int = 30, retry_delay: int = 2) -> bool:
        """
        Wait for PostgreSQL to be ready
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Waiting for PostgreSQL to be ready...")
        
        for attempt in range(1, max_retries + 1):
            try:
                conn = psycopg2.connect(**self.db_config)
                conn.close()
                logger.info(f"✓ PostgreSQL is ready (attempt {attempt}/{max_retries})")
                return True
            except psycopg2.OperationalError as e:
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to PostgreSQL after maximum retries")
                    return False
        
        return False
    
    def connect(self) -> bool:
        """
        Establish database connection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info(f"✓ Connected to database: {self.db_config['database']}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def check_tables_exist(self) -> bool:
        """
        Check if required tables already exist
        
        Returns:
            True if tables exist, False otherwise
        """
        required_tables = [
            'brands', 'characters', 'character_clips', 'video_scripts',
            'videos', 'performance_analytics', 'products', 'posting_schedule',
            'system_config', 'audit_logs'
        ]
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                missing_tables = set(required_tables) - set(existing_tables)
                
                if not missing_tables:
                    logger.info(f"✓ All required tables exist: {len(required_tables)} tables")
                    return True
                else:
                    logger.info(f"Missing tables: {missing_tables}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to check tables: {e}")
            return False
    
    def run_schema_sql(self) -> bool:
        """
        Execute the schema.sql file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.schema_file.exists():
            logger.error(f"Schema file not found: {self.schema_file}")
            return False
        
        try:
            logger.info(f"Reading schema file: {self.schema_file}")
            with open(self.schema_file, 'r') as f:
                schema_sql = f.read()
            
            logger.info("Executing schema SQL...")
            with self.connection.cursor() as cursor:
                cursor.execute(schema_sql)
            
            logger.info("✓ Schema executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute schema: {e}")
            return False
    
    def verify_setup(self) -> bool:
        """
        Verify database setup by checking tables, indexes, and functions
        
        Returns:
            True if verification successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                # Count tables
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """)
                table_count = cursor.fetchone()[0]
                
                # Count indexes
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_indexes 
                    WHERE schemaname = 'public'
                """)
                index_count = cursor.fetchone()[0]
                
                # Count views
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.views 
                    WHERE table_schema = 'public'
                """)
                view_count = cursor.fetchone()[0]
                
                # Count triggers
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.triggers 
                    WHERE trigger_schema = 'public'
                """)
                trigger_count = cursor.fetchone()[0]
                
                # Check system_config entries
                cursor.execute("SELECT COUNT(*) FROM system_config")
                config_count = cursor.fetchone()[0]
                
                logger.info("=" * 50)
                logger.info("DATABASE VERIFICATION SUMMARY")
                logger.info("=" * 50)
                logger.info(f"✓ Tables:    {table_count}")
                logger.info(f"✓ Indexes:   {index_count}")
                logger.info(f"✓ Views:     {view_count}")
                logger.info(f"✓ Triggers:  {trigger_count}")
                logger.info(f"✓ Config:    {config_count} entries")
                logger.info("=" * 50)
                
                # Verify minimum requirements
                if table_count < 9:
                    logger.error(f"Expected at least 9 tables, found {table_count}")
                    return False
                
                if config_count < 1:
                    logger.error("No system configuration entries found")
                    return False
                
                logger.info("✓ Database verification passed")
                return True
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def insert_sample_data(self) -> bool:
        """
        Insert minimal sample data for testing (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                # Check if sample brand already exists
                cursor.execute("SELECT COUNT(*) FROM brands WHERE name = 'Sample Brand'")
                if cursor.fetchone()[0] > 0:
                    logger.info("Sample data already exists, skipping...")
                    return True
                
                # Insert sample brand
                cursor.execute("""
                    INSERT INTO brands (name, niche, tonality, target_audience, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    'Sample Brand',
                    'Technology',
                    'Professional',
                    'Tech enthusiasts aged 25-40',
                    'active'
                ))
                
                logger.info("✓ Sample data inserted successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to insert sample data: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def run(self, skip_if_exists: bool = True, insert_samples: bool = False) -> bool:
        """
        Run the complete initialization process
        
        Args:
            skip_if_exists: Skip schema execution if tables exist
            insert_samples: Insert sample data after initialization
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 50)
        logger.info("KIVerdienst v2 Database Initialization")
        logger.info("=" * 50)
        
        try:
            # Step 1: Wait for database
            if not self.wait_for_database():
                return False
            
            # Step 2: Connect
            if not self.connect():
                return False
            
            # Step 3: Check if tables exist
            tables_exist = self.check_tables_exist()
            
            # Step 4: Run schema if needed
            if tables_exist and skip_if_exists:
                logger.info("Tables already exist, skipping schema execution")
            else:
                if not self.run_schema_sql():
                    return False
            
            # Step 5: Verify setup
            if not self.verify_setup():
                return False
            
            # Step 6: Insert sample data (optional)
            if insert_samples:
                self.insert_sample_data()
            
            logger.info("=" * 50)
            logger.info("✓ DATABASE INITIALIZATION COMPLETE")
            logger.info("=" * 50)
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
        finally:
            self.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize KIVerdienst v2 Database')
    parser.add_argument('--force', action='store_true', 
                       help='Force re-run schema even if tables exist')
    parser.add_argument('--samples', action='store_true',
                       help='Insert sample data')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check database connectivity')
    
    args = parser.parse_args()
    
    try:
        initializer = DatabaseInitializer()
        
        if args.check_only:
            # Just check connection
            if initializer.wait_for_database():
                logger.info("✓ Database is accessible")
                sys.exit(0)
            else:
                logger.error("✗ Cannot connect to database")
                sys.exit(1)
        else:
            # Full initialization
            success = initializer.run(
                skip_if_exists=not args.force,
                insert_samples=args.samples
            )
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
