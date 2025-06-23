#!/usr/bin/env python3
"""
Database initialization utility for pAInt project.
Runs migrations and seeds data.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection from environment variables."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "paint_user"),
        password=os.getenv("POSTGRES_PASSWORD", "paint_password"),
        database=os.getenv("POSTGRES_DB", "paint_catalog"),
    )


def run_sql_file(connection, file_path):
    """Execute SQL file."""
    try:
        with open(file_path, "r") as file:
            sql_content = file.read()

        cursor = connection.cursor()
        cursor.execute(sql_content)
        connection.commit()
        cursor.close()
        logger.info(f"Successfully executed: {file_path}")

    except Exception as e:
        logger.error(f"Error executing {file_path}: {e}")
        connection.rollback()
        raise


def initialize_database():
    """Initialize database with migrations and seed data."""
    try:
        # Connect to database
        connection = get_db_connection()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        logger.info("Connected to database successfully")

        # Run migrations
        migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        seeds_dir = os.path.join(os.path.dirname(__file__), "seeds")

        # Execute migration files in order
        migration_files = sorted(
            [f for f in os.listdir(migrations_dir) if f.endswith(".sql")]
        )
        for migration_file in migration_files:
            migration_path = os.path.join(migrations_dir, migration_file)
            logger.info(f"Running migration: {migration_file}")
            run_sql_file(connection, migration_path)

        # Execute seed files in order
        seed_files = sorted([f for f in os.listdir(seeds_dir) if f.endswith(".sql")])
        for seed_file in seed_files:
            seed_path = os.path.join(seeds_dir, seed_file)
            logger.info(f"Running seed: {seed_file}")
            run_sql_file(connection, seed_path)

        connection.close()
        logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_database_connection():
    """Test database connection."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            logger.info("Database connection test: SUCCESS")
            return True
        else:
            logger.error("Database connection test: FAILED")
            return False

    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test connection only
        success = check_database_connection()
        sys.exit(0 if success else 1)
    else:
        # Full initialization
        initialize_database()
