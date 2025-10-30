from flask import Blueprint, request, jsonify, g
from app.database.models.user import User
from app.database.auth import auth_required, create_token
from app.database.db import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Create user
        user = User.create_user(username=username, email=email, password_hash=password)
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Create JWT token
        access_token = create_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logger.error(f'Registration failed: {str(e)}')
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        user = User.authenticate(email, password)

        print("Authenticated user:", user)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        access_token = create_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f'Login failed: {str(e)}')
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    """Logout user (JWT tokens are stateless, so this just returns success)"""
    try:
        return jsonify({
            'success': True, 
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Logout failed: {str(e)}')
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_profile():
    """Get current user profile"""
    try:
        current_user = User.query.get(request.user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Failed to get profile: {str(e)}')
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/me', methods=['PUT'])
@auth_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_user = User.query.get(request.user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Fields that can be updated
        allowed_fields = ['username', 'email']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                value = data[field].strip() if isinstance(data[field], str) else data[field]
                if value:
                    update_data[field] = value
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Check for duplicates
        if 'username' in update_data:
            existing_user = User.query.filter_by(username=update_data['username']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Username already exists'}), 400
        
        if 'email' in update_data:
            existing_user = User.query.filter_by(email=update_data['email']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update user
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Profile update failed: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Profile update failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@auth_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        current_user = User.query.get(request.user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Change password
        current_user.hash_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Password change failed: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Password change failed'}), 500