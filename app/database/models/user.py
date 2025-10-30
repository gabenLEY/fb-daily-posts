"""
User model for authentication and user management
"""
import hashlib
import secrets
from datetime import datetime
from app.database.db import db

class User(db.Model):
    """User model with JWT-based authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Facebook integration fields
    facebook_data = db.Column(db.Text)  # JSON string with user's Facebook data
    selected_page_id = db.Column(db.String(50))  # Currently selected Facebook page ID
    selected_page_token = db.Column(db.Text)  # Access token for selected page
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = db.relationship("Post", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        try:
            salt, hash_part = password_hash.split('$')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == hash_part
        except ValueError:
            return False
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = User.hash_password(password)
    
    def check_password(self, password):
        """Check user password"""
        return self.verify_password(password, self.password_hash)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_user(cls, username, email, password):
        """Create a new user"""
        try:
            user = cls(
                username=username,
                email=email
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        return cls.query.filter_by(id=user_id).first()
    
    @classmethod
    def authenticate(cls, username_or_email, password):
        """Authenticate user with username/email and password"""
        # Try to find user by username first, then email
        user = cls.get_by_username(username_or_email)
        if not user:
            user = cls.get_by_email(username_or_email)
        
        if user and user.is_active and user.check_password(password):
            return user
        return None