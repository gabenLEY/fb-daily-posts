#!/usr/bin/env python3
"""
Test database connection and initialize tables
"""
import os
import logging
from app import create_app
from app.database.db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and create tables if needed"""
    logger.info("🗄️ Testing database connection...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic connection
            db.engine.connect()
            logger.info("✅ Database connection successful!")
            
            # Import models
            from app.database.models.user import User
            from app.database.models.post import Post
            
            # Create tables
            db.create_all()
            logger.info("✅ Database tables created/verified!")
            
            # Test a simple query
            user_count = User.query.count()
            logger.info(f"📊 Users in database: {user_count}")
            
            # Show database URL (masked)
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' in db_url:
                logger.info(f"🐘 Using PostgreSQL database")
            else:
                logger.info(f"💾 Using SQLite database")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            logger.error(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')[:50]}...")
            return False

if __name__ == '__main__':
    success = test_database_connection()
    if success:
        print("✅ Database is ready!")
    else:
        print("❌ Database connection failed!")
        exit(1)