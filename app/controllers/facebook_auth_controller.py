"""
Facebook Authentication Controller
Allows users to connect their Facebook pages to the app
"""
from flask import Blueprint, request, jsonify, redirect, url_for, session
import requests
import os
from app.database.models.user import User
from app.database.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

facebook_auth_bp = Blueprint('facebook_auth', __name__)

@facebook_auth_bp.route('/facebook/login-url', methods=['GET', 'POST'])
@jwt_required()
def get_facebook_login_url():
    """Generate Facebook login URL for page access"""
    try:
        # Get current user from JWT
        user_id = get_jwt_identity()
        
        app_id = os.getenv('FB_APP_ID')
        redirect_uri = os.getenv('FB_REDIRECT_URI', 'http://127.0.0.1:8000/api/facebook-auth/callback')
        
        if not app_id:
            return jsonify({'error': 'Facebook App ID not configured'}), 500
        
        # Required permissions for page management
        scope = 'pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_metadata'
        
        facebook_login_url = (
            f"https://www.facebook.com/v19.0/dialog/oauth?"
            f"client_id={app_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"state={user_id}"  # Use user ID as state for security
        )
        
        return jsonify({
            'success': True,
            'login_url': facebook_login_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate login URL: {str(e)}'}), 500

@facebook_auth_bp.route('/callback', methods=['GET'])
def facebook_callback():
    """Handle Facebook OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # This should be the user ID
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'Facebook authorization failed: {error}'}), 400
        
        if not code or not state:
            return jsonify({'error': 'Missing authorization code or state'}), 400
        
        # Verify user exists
        user = User.query.get(int(state))
        if not user:
            return jsonify({'error': 'Invalid user'}), 400
        
        # Exchange code for access token
        app_id = os.getenv('FB_APP_ID')
        app_secret = os.getenv('FB_APP_SECRET')
        redirect_uri = os.getenv('FB_REDIRECT_URI', 'http://127.0.0.1:8000/api/facebook-auth/callback')
        
        token_url = (
            f"https://graph.facebook.com/v19.0/oauth/access_token?"
            f"client_id={app_id}&"
            f"client_secret={app_secret}&"
            f"redirect_uri={redirect_uri}&"
            f"code={code}"
        )
        
        token_response = requests.get(token_url)
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            return jsonify({'error': 'Failed to get access token', 'details': token_data}), 400
        
        user_access_token = token_data['access_token']
        
        # Get user's pages
        pages_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={user_access_token}"
        pages_response = requests.get(pages_url)
        pages_data = pages_response.json()
        
        if 'data' not in pages_data:
            return jsonify({'error': 'Failed to get user pages', 'details': pages_data}), 400
        
        # Store Facebook credentials for user
        facebook_data = {
            'user_access_token': user_access_token,
            'pages': pages_data['data']
        }
        
        # Update user with Facebook data
        user.facebook_data = json.dumps(facebook_data)
        db.session.commit()
        
        # Redirect to frontend with success
        frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:3000')
        return redirect(f"{frontend_url}/dashboard?facebook_connected=true")
        
    except Exception as e:
        return jsonify({'error': f'Callback failed: {str(e)}'}), 500

@facebook_auth_bp.route('/pages', methods=['GET'])
@jwt_required()
def get_user_pages():
    """Get user's Facebook pages"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.facebook_data:
            return jsonify({'error': 'Facebook not connected'}), 400
        
        facebook_data = json.loads(user.facebook_data)
        pages = facebook_data.get('pages', [])
        
        # Format pages for frontend
        formatted_pages = []
        for page in pages:
            formatted_pages.append({
                'id': page['id'],
                'name': page['name'],
                'access_token': page['access_token'][:10] + '...' + page['access_token'][-4:],  # Masked for security
                'category': page.get('category', ''),
                'tasks': page.get('tasks', [])
            })
        
        return jsonify({
            'success': True,
            'pages': formatted_pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get pages: {str(e)}'}), 500

@facebook_auth_bp.route('/select-page', methods=['POST'])
@jwt_required()
def select_page():
    """Select a Facebook page for posting"""
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        
        if not page_id:
            return jsonify({'error': 'Page ID required'}), 400
        
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.facebook_data:
            return jsonify({'error': 'Facebook not connected'}), 400
        
        facebook_data = json.loads(user.facebook_data)
        pages = facebook_data.get('pages', [])
        
        # Find selected page
        selected_page = None
        for page in pages:
            if page['id'] == page_id:
                selected_page = page
                break
        
        if not selected_page:
            return jsonify({'error': 'Page not found'}), 404
        
        # Store selected page info
        user.selected_page_id = page_id
        user.selected_page_token = selected_page['access_token']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Page selected successfully',
            'page': {
                'id': selected_page['id'],
                'name': selected_page['name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to select page: {str(e)}'}), 500

@facebook_auth_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect_facebook():
    """Disconnect Facebook from user account"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Clear Facebook data
        user.facebook_data = None
        user.selected_page_id = None
        user.selected_page_token = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Facebook disconnected successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to disconnect: {str(e)}'}), 500