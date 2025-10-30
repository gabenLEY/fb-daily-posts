from flask import Blueprint, request, jsonify
from app.database.auth import auth_required, auth_optional
from app.database.models.post import Post
from app.database.models.user import User
from app.database.db import db
import os
import base64
import requests
from datetime import datetime
import logging

# Import existing providers
try:
    from app.providers.llama_meta import refine_prompt_and_captions
    print("✅ Real llama_meta provider loaded successfully")
except ImportError as e:
    print(f"⚠️  Failed to import llama_meta provider: {e}")
    def refine_prompt_and_captions(topic, style):
        return {
            'prompt': f"A {style} of {topic}",
            'captions': [f"Check out this {topic}!", f"Amazing {topic} content"]
        }

try:
    from app.providers.image_gen import generate_image
    print("✅ Real image_gen provider loaded successfully")
except ImportError as e:
    print(f"⚠️  Failed to import image_gen provider: {e}")
    print("🔄 Using mock image generation (placeholder images)")
    def generate_image(prompt, size='1024x1024', add_watermark=True):
        return {
            'image_url': 'https://via.placeholder.com/1024x1024',
            'b64_image': None
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

social_bp = Blueprint('social', __name__)

@social_bp.route('/generate-prompt', methods=['POST'])
@auth_optional
def generate_prompt():
    """Generate AI prompt and captions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        topic = data.get('topic', '').strip()
        style = data.get('style', 'clean product shot').strip()
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate prompt and captions
        result = refine_prompt_and_captions(topic, style)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f'Failed to generate prompt: {str(e)}')
        return jsonify({'error': 'Failed to generate prompt'}), 500

# Compatibility route for old endpoint
@social_bp.route('/prompt', methods=['POST', 'OPTIONS'])
@auth_optional
def generate_prompt_compat():
    """Generate AI prompt and captions (compatibility endpoint)"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    # Same logic as generate_prompt but for compatibility
    return generate_prompt()

@social_bp.route('/generate-image', methods=['POST'])
@auth_optional
def generate_image_endpoint():
    """Generate AI image"""
    logger.info("🖼️  POST /api/generate-image endpoint called")
    
    try:
        # Debug: Log request details
        logger.info(f"📝 Request method: {request.method}")
        logger.info(f"📝 Request headers: {dict(request.headers)}")
        logger.info(f"📝 Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.info(f"📝 Raw request data: {data}")
        
        if not data:
            logger.warning("❌ No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        size = data.get('size', '1024x1024')
        
        logger.info(f"📝 Extracted prompt: '{prompt}'")
        logger.info(f"📝 Extracted size: '{size}'")
        
        if not prompt:
            logger.warning("❌ Prompt is empty or missing")
            return jsonify({'error': 'Prompt is required'}), 400
        
        logger.info(f"✅ Valid request - generating image for prompt: '{prompt}'")
        
        # Generate image
        result = generate_image(prompt, size=size, add_watermark=True)
        
        logger.info(f"✅ Image generation successful: {result}")
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f'💥 Failed to generate image: {str(e)}')
        logger.error(f'💥 Exception type: {type(e).__name__}')
        import traceback
        logger.error(f'💥 Traceback: {traceback.format_exc()}')
        return jsonify({'error': 'Failed to generate image'}), 500

@social_bp.route('/publish-facebook', methods=['POST'])
@auth_required
def publish_to_facebook():
    """Publish post to Facebook"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_user_id = request.user_id
        post_id = data.get('post_id')
        b64_png = data.get('b64_png')
        caption = data.get('caption', '')
        publish_now = bool(data.get('publish_now', True))
        
        # Get post if post_id provided
        post = None
        if post_id:
            post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
            if not post:
                return jsonify({'error': 'Post not found or permission denied'}), 404
            
            # Use post data if not provided in request
            if not caption:
                caption = post.content
            if not b64_png and hasattr(post, 'image_data'):
                b64_png = post.image_data
        
        if not b64_png:
            return jsonify({'error': 'Image data is required'}), 400
        
        if not caption:
            return jsonify({'error': 'Caption is required'}), 400
        
        # Get user's Facebook credentials
        from app.database.models.user import User
        user = User.query.get(current_user_id)
        
        # Check if user has selected a Facebook page
        if user.selected_page_id and user.selected_page_token:
            page_id = user.selected_page_id
            token = user.selected_page_token
        else:
            # Fallback to environment variables (for backwards compatibility)
            page_id = os.getenv("FB_PAGE_ID")
            token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        
        if not (page_id and token):
            return jsonify({
                'error': 'Facebook page not connected',
                'message': 'Please connect your Facebook page first'
            }), 400
        
        try:
            # Decode base64 image
            image_data = base64.b64decode(b64_png)
            
            # Upload photo to Facebook
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            
            files = {
                'source': ('image.png', image_data, 'image/png')
            }
            
            params = {
                'access_token': token,
                'message': caption,
                'published': 'true' if publish_now else 'false'
            }
            
            response = requests.post(url, files=files, data=params)
            response_data = response.json()
            
            if response.status_code == 200 and 'id' in response_data:
                # Update post status if we have a post record
                if post:
                    post.status = 'published' if publish_now else 'scheduled'
                    post.published_at = datetime.utcnow() if publish_now else None
                    post.platform_post_id = response_data['id']
                    db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Post published successfully' if publish_now else 'Post scheduled successfully',
                    'facebook_post_id': response_data['id'],
                    'post_url': f"https://www.facebook.com/{response_data['id']}"
                }), 200
            else:
                logger.error(f'Facebook API error: {response_data}')
                return jsonify({
                    'error': 'Failed to publish to Facebook',
                    'details': response_data.get('error', {}).get('message', 'Unknown error')
                }), 400
                
        except Exception as e:
            logger.error(f'Facebook publishing error: {str(e)}')
            return jsonify({'error': 'Failed to publish to Facebook'}), 500
        
    except Exception as e:
        logger.error(f'Publish to Facebook failed: {str(e)}')
        return jsonify({'error': 'Publish to Facebook failed'}), 500

@social_bp.route('/save-draft', methods=['POST'])
@auth_required
def save_draft():
    """Save post as draft"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_user_id = request.user_id
        content = data.get('content', '').strip()
        image_data = data.get('image_data')  # base64 encoded image
        scheduled_time = data.get('scheduled_time')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Create draft post
        post = Post.create_post(
            user_id=current_user_id,
            content=content,
            platform='facebook',
            scheduled_time=scheduled_time,
            status='draft'
        )
        
        if not post:
            return jsonify({'error': 'Failed to save draft'}), 500
        
        # Store image data if provided (you might want to save this to file system or cloud storage)
        if image_data:
            # For now, we'll just indicate that image data exists
            # In a real application, you'd save this to storage and store the URL
            post.media_urls = ['image_data_present']
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Draft saved successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Save draft failed: {str(e)}')
        return jsonify({'error': 'Failed to save draft'}), 500

@social_bp.route('/schedule-post', methods=['POST'])
@auth_required
def schedule_post():
    """Schedule a post for later publishing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_user_id = request.user_id
        content = data.get('content', '').strip()
        scheduled_time = data.get('scheduled_time')
        image_data = data.get('image_data')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if not scheduled_time:
            return jsonify({'error': 'Scheduled time is required'}), 400
        
        try:
            # Parse scheduled time
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            if scheduled_dt <= datetime.utcnow():
                return jsonify({'error': 'Scheduled time must be in the future'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid scheduled time format'}), 400
        
        # Create scheduled post
        post = Post.create_post(
            user_id=current_user_id,
            content=content,
            platform='facebook',
            scheduled_time=scheduled_dt,
            status='scheduled'
        )
        
        if not post:
            return jsonify({'error': 'Failed to schedule post'}), 500
        
        # Store image data if provided
        if image_data:
            post.media_urls = ['image_data_present']
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post scheduled successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Schedule post failed: {str(e)}')
        return jsonify({'error': 'Failed to schedule post'}), 500

@social_bp.route('/facebook-config', methods=['GET'])
@auth_required
def get_facebook_config():
    """Get Facebook configuration status"""
    try:
        page_id = os.getenv("FB_PAGE_ID")
        token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        
        return jsonify({
            'success': True,
            'configured': bool(page_id and token),
            'page_id': page_id if page_id else None
        }), 200
        
    except Exception as e:
        logger.error(f'Get Facebook config failed: {str(e)}')
        return jsonify({'error': 'Failed to get Facebook configuration'}), 500