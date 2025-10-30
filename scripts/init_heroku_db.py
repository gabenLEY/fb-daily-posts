#!/usr/bin/env python3
"""
Heroku database initialization script
Run this after deploying to set up the database tables
"""
import os
import sys
from app import create_app
from app.database.db import db

def init_heroku_database():
    """Initialize database tables on Heroku"""
    print("🗄️ Initializing Heroku PostgreSQL database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Import all models to ensure they are registered
            from app.database.models.user import User
            from app.database.models.post import Post
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            print(f"📊 Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Check if tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables created: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)

if __name__ == '__main__':
    init_heroku_database()