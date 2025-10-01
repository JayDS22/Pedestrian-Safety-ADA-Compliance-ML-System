"""
Initialize PostgreSQL database with PostGIS extension
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import os
from dotenv import load_load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database():
    """Create database if it doesn't exist"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="ada_user",
        password="ada_password",
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='ada_compliance'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("CREATE DATABASE ada_compliance")
        logger.info("Database 'ada_compliance' created")
    else:
        logger.info("Database 'ada_compliance' already exists")
    
    cursor.close()
    conn.close()


def setup_postgis():
    """Enable PostGIS extension"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="ada_user",
        password="ada_password",
        database="ada_compliance"
    )
    
    cursor = conn.cursor()
    
    # Enable PostGIS
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    logger.info("PostGIS extension enabled")
    
    conn.commit()
    cursor.close()
    conn.close()


def create_tables():
    """Create database tables"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="ada_user",
        password="ada_password",
        database="ada_compliance"
    )
    
    cursor = conn.cursor()
    
    # Assessments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id SERIAL PRIMARY KEY,
            location VARCHAR(255),
            location_geom GEOMETRY(Point, 4326),
            compliance_score INTEGER,
            total_violations INTEGER,
            total_cost DECIMAL(10, 2),
            estimated_timeline VARCHAR(50),
            image_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Violations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id SERIAL PRIMARY KEY,
            assessment_id INTEGER REFERENCES assessments(id),
            violation_type VARCHAR(100),
            severity VARCHAR(20),
            priority INTEGER,
            detected_value VARCHAR(100),
            standard_value VARCHAR(100),
            cost DECIMAL(10, 2),
            location VARCHAR(255),
            location_geom GEOMETRY(Point, 4326),
            recommendation TEXT,
            reference VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_location ON assessments USING GIST(location_geom)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_location ON violations USING GIST(location_geom)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_priority ON violations(priority)")
    
    logger.info("Database tables created")
    
    conn.commit()
    cursor.close()
    conn.close()


def main():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        create_database()
        setup_postgis()
        create_tables()
        logger.info("Database initialization complete!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    main()
