"""
Database migration script to add Facebook fields to User model
Run this script to update existing database with new Facebook integration fields
"""

import sys
import os

# Add the parent directory to Python path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database.db import db
from app.database.models.user import User

def migrate_user_facebook_fields():
    """Add Facebook integration fields to existing User table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy import text, inspect
            
            # Check if we need to create the columns
            inspector = inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('users')]
            
            # Add Facebook data column if it doesn't exist
            if 'facebook_data' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE users ADD COLUMN facebook_data TEXT'))
                    conn.commit()
                print("✅ Added facebook_data column")
            
            # Add selected page ID column if it doesn't exist  
            if 'selected_page_id' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE users ADD COLUMN selected_page_id VARCHAR(50)'))
                    conn.commit()
                print("✅ Added selected_page_id column")
            
            # Add selected page token column if it doesn't exist
            if 'selected_page_token' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE users ADD COLUMN selected_page_token TEXT'))
                    conn.commit()
                print("✅ Added selected_page_token column")
            
            print("🎉 User table migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting User table migration...")
    success = migrate_user_facebook_fields()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")