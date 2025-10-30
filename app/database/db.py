"""
Database configuration with Flask-SQLAlchemy and PostgreSQL
"""
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def handle_database_error(func):
    """Decorator to handle database connection errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Database error in {func.__name__}: {e}")
            # Try to reconnect
            try:
                db.session.rollback()
                db.session.close()
            except:
                pass
            raise e
    return wrapper

def get_database_url():
    """Get database URL from environment variables with fallback to SQLite"""
    # First, check for Heroku's DATABASE_URL (PostgreSQL)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Heroku uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Check if manual PostgreSQL configuration is available
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if all([db_host, db_name, db_user, db_password]):
        # PostgreSQL configuration
        return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        # Fallback to SQLite for development
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'data', 'app.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f'sqlite:///{db_path}'

def init_database(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Configure robust PostgreSQL connection handling for Heroku
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    if database_uri and (database_uri.startswith('postgresql://') or database_uri.startswith('postgres://')):
        # Heroku PostgreSQL configuration
        engine_options = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 0,
            'pool_size': 5,
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 10,
                'application_name': 'fb-daily-posts'
            }
        }
    else:
        # Local development configuration
        engine_options = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    
    db.init_app(app)
    
    # Import all models to ensure they are registered
    from app.database.models.user import User
    from app.database.models.post import Post
    from app.database.models.job import Job
    
    with app.app_context():
        db.create_all()
        print(f"Database initialized: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    return db