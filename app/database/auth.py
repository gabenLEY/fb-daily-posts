"""
JWT Authentication utilities
"""
import os
from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
from app.database.models.user import User

jwt = JWTManager()

def init_jwt(app):
    """Initialize JWT manager with Flask app"""
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key-change-this')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire by default
    jwt.init_app(app)
    return jwt

@jwt.user_identity_loader
def user_identity_lookup(user):
    """Define how to extract user identity for JWT"""
    # Handle both user objects and user IDs
    if hasattr(user, 'id'):
        return user.id
    else:
        return user  # Assume it's already a user ID

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from JWT token"""
    identity = jwt_data["sub"]
    return User.get_by_id(int(identity))

def create_token(user):
    """Create JWT access token for user"""
    return create_access_token(identity=user)

def auth_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user = get_jwt_identity()
            user = User.get_by_id(current_user)
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid or inactive user'}), 401
            g.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    return decorated_function

def auth_optional(f):
    """Decorator for optional JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            if current_user_id:
                user = User.get_by_id(current_user_id)
                if user and user.is_active:
                    g.current_user = user
                else:
                    g.current_user = None
            else:
                g.current_user = None
        except Exception:
            g.current_user = None
        return f(*args, **kwargs)
    return decorated_function