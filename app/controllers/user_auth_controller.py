"""
User Authentication Controller with Facebook Integration
Handles user registration, login, and Facebook connection
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.database.db import db
from app.database.models.user import User
import json
import re

# Create Blueprint
user_auth_bp = Blueprint('user_auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

@user_auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        connect_facebook = data.get('connect_facebook', False)
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'error': 'Username, email, and password are required'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        response_data = {
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'facebook_connected': bool(user.facebook_data)
            },
            'access_token': access_token
        }
        
        # If user wants to connect Facebook immediately
        if connect_facebook:
            response_data['next_step'] = 'connect_facebook'
            response_data['facebook_login_url'] = f'/api/facebook-auth/facebook/login-url'
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500

@user_auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with username/email and password"""
    try:
        data = request.get_json()
        
        # Get login credentials
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not all([username_or_email, password]):
            return jsonify({
                'success': False,
                'error': 'Username/email and password are required'
            }), 400
        
        # Authenticate user
        user = User.authenticate(username_or_email.lower() if validate_email(username_or_email) else username_or_email, password)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        # Parse Facebook data if it exists
        facebook_data = None
        if user.facebook_data:
            try:
                facebook_data = json.loads(user.facebook_data)
            except:
                facebook_data = None
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'facebook_connected': bool(user.facebook_data),
                'selected_page_id': user.selected_page_id,
                'facebook_pages': facebook_data.get('pages', []) if facebook_data else []
            },
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@user_auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Parse Facebook data if it exists
        facebook_data = None
        if user.facebook_data:
            try:
                facebook_data = json.loads(user.facebook_data)
            except:
                facebook_data = None
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'facebook_connected': bool(user.facebook_data),
                'selected_page_id': user.selected_page_id,
                'facebook_pages': facebook_data.get('pages', []) if facebook_data else [],
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get profile: {str(e)}'
        }), 500

@user_auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Update username if provided
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                # Check if username is already taken
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'error': 'Username already exists'
                    }), 409
                user.username = new_username
        
        # Update email if provided
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if not validate_email(new_email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400
            
            if new_email != user.email:
                # Check if email is already taken
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'error': 'Email already registered'
                    }), 409
                user.email = new_email
        
        # Update password if provided
        if 'password' in data:
            new_password = data['password']
            is_valid, message = validate_password(new_password)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400
            user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'facebook_connected': bool(user.facebook_data)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to update profile: {str(e)}'
        }), 500

@user_auth_bp.route('/facebook-connection-status', methods=['GET'])
@jwt_required()
def facebook_connection_status():
    """Get Facebook connection status for current user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Parse Facebook data if it exists
        facebook_data = None
        if user.facebook_data:
            try:
                facebook_data = json.loads(user.facebook_data)
            except:
                facebook_data = None
        
        return jsonify({
            'success': True,
            'facebook_connected': bool(user.facebook_data),
            'selected_page_id': user.selected_page_id,
            'facebook_pages': facebook_data.get('pages', []) if facebook_data else [],
            'next_step': 'connect_facebook' if not user.facebook_data else 'ready_to_post'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get Facebook status: {str(e)}'
        }), 500