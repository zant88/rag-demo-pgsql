#!/usr/bin/env python3
"""
Database initialization script for Docker deployment.
This script creates all tables and runs any necessary setup.
"""

import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import Base
from app.models import document, chunk, knowledge  # Import all models


def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be available."""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}). Waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                sys.exit(1)
    
    return engine


def create_tables(engine):
    """Create all database tables."""
    try:
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)


def setup_pgvector_extension(engine):
    """Set up pgvector extension if using PostgreSQL."""
    try:
        if "postgresql" in settings.SQLALCHEMY_DATABASE_URI:
            print("🔧 Setting up pgvector extension...")
            with engine.connect() as conn:
                # Enable pgvector extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            print("✅ pgvector extension enabled!")
    except Exception as e:
        print(f"⚠️  Warning: Could not set up pgvector extension: {e}")
        print("This might be normal if the extension is already enabled or not needed.")


if __name__ == "__main__":
    print("🚀 Initializing database...")
    print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Wait for database to be available
    engine = wait_for_db()
    
    # Set up pgvector extension
    setup_pgvector_extension(engine)
    
    # Create all tables
    create_tables(engine)
    
    print("🎉 Database initialization completed!")