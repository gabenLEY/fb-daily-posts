from flask import Blueprint, request, jsonify
from app.database.auth import auth_required, auth_optional
from app.database.models.post import Post
from app.database.models.user import User
from app.database.db import db
from flask_jwt_extended import get_jwt_identity
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
    """Generate AI image (chunked timeout approach)"""
    logger.info("🖼️  POST /api/generate-image endpoint called")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        size = data.get('size', '1024x1024')
        attempt = int(data.get('attempt', 1))
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        logger.info(f"🎨 Image generation attempt {attempt} for: '{prompt[:50]}...'")
        
        # Forward to simple image controller
        from app.controllers.simple_image_controller import try_generate_with_timeout, try_generate_dalle2, generate_placeholder
        
        # Try different strategies based on attempt number
        if attempt == 1:
            # First attempt: Try with shorter timeout
            result = try_generate_with_timeout(prompt, size, timeout=25)
        elif attempt == 2:
            # Second attempt: Try with DALL-E 2 (faster)
            result = try_generate_dalle2(prompt, size, timeout=25)
        else:
            # Third attempt: Return placeholder
            result = generate_placeholder(prompt, size)
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'attempt': attempt
            }), 200
        else:
            # Suggest retry with next strategy
            return jsonify({
                'success': False,
                'message': f'Attempt {attempt} timed out, try again for next strategy',
                'next_attempt': attempt + 1,
                'retry_suggestion': 'Call same endpoint with "attempt": ' + str(attempt + 1)
            }), 202
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Failed to generate image: {error_msg}')
        
        return jsonify({
            'error': 'Failed to generate image',
            'message': str(e),
            'suggestion': 'Please try again'
        }), 500

@social_bp.route('/generate-image-async', methods=['POST'])
@auth_optional
def generate_image_async():
    """Start async image generation job"""
    logger.info("🎨 POST /api/generate-image-async endpoint called")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        size = data.get('size', '1024x1024')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Start async job
        from app.utils.job_queue import start_image_generation_job
        job_id = start_image_generation_job(prompt, size)
        
        logger.info(f"✅ Started async image generation job: {job_id}")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'processing',
            'message': 'Image generation started. Use /api/social/job-status/{job_id} to check progress.'
        }), 202
        
    except Exception as e:
        logger.error(f'💥 Failed to start async job: {str(e)}')
        return jsonify({'error': 'Failed to start image generation'}), 500

@social_bp.route('/job-status/<job_id>', methods=['GET', 'OPTIONS'])
@auth_optional
def get_job_status(job_id):
    """Get job status and result"""
    from flask import request, jsonify
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        logger.info(f"🔍 Checking job status for ID: {job_id}")
        from app.utils.job_queue import job_queue
        
        job = job_queue.get_job(job_id)
        if not job:
            logger.warning(f"❌ Job not found: {job_id}")
            return jsonify({'error': 'Job not found'}), 404
        
        logger.info(f"✅ Job found: {job_id} - Status: {job.get('status', 'unknown')}")
        
        response_data = {
            'job_id': job['id'],
            'status': job['status'],
            'created_at': job['created_at'].isoformat(),
            'updated_at': job['updated_at'].isoformat()
        }
        
        if job['status'] == 'completed':
            response_data['result'] = job['result']
        elif job['status'] == 'failed':
            response_data['error'] = job['error']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f'💥 Failed to get job status: {str(e)}')
        return jsonify({'error': 'Failed to get job status'}), 500

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
            
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401
            
        post_id = data.get('post_id')
        b64_png = data.get('b64_png')
        caption = data.get('caption', '')
        publish_now = bool(data.get('publish_now', True))
        
        # Get post from database only if NOT publishing now (i.e., for scheduled posts)
        post = None
        if post_id and not publish_now:
            # Only try to retrieve post from database for scheduled posts
            try:
                # Check if post_id is a valid database ID (not a Facebook post ID)
                post_id_int = int(post_id)
                if post_id_int > 2147483647:  # PostgreSQL integer max value
                    # This is likely a Facebook post ID, not our database post ID
                    logger.warning(f"⚠️ Received Facebook post ID ({post_id}) instead of database post ID - ignoring")
                    post_id = None
                    post = None
                else:
                    post = Post.query.filter_by(id=post_id_int, user_id=current_user_id).first()
                    if not post:
                        return jsonify({'error': 'Post not found or permission denied'}), 404
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid post_id format: {post_id} - ignoring")
                post_id = None
                post = None
        elif post_id and publish_now:
            # If publish_now is true, ignore post_id - this is immediate publishing
            logger.info("� Immediate publish - ignoring post_id parameter")
            post_id = None
            post = None
            
        # Use post data if we have a valid post record
        if post:
            # Use post data if not provided in request
            if not caption:
                caption = post.content
            if not b64_png and hasattr(post, 'image_data'):
                b64_png = post.image_data
        
        # Check if we have either image or caption for Facebook post
        if not b64_png and not caption:
            return jsonify({'error': 'Either image data or caption is required'}), 400
        
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
            if b64_png:
                # Post with image
                logger.info("📸 Publishing post with image to Facebook")
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
            else:
                # Text-only post
                logger.info("📝 Publishing text-only post to Facebook")
                url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
                
                params = {
                    'access_token': token,
                    'message': caption,
                    'published': 'true' if publish_now else 'false'
                }
                
                response = requests.post(url, data=params)
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
            
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401
            
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
    """Schedule a post for later publishing directly to Facebook"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401
            
        content = data.get('content', '').strip()
        scheduled_time = data.get('scheduled_time')
        facebook_page_id = data.get('facebook_page_id')
        image_data = data.get('image_data')  # base64 encoded image
        b64_png = data.get('b64_png')  # Alternative image format
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if not scheduled_time:
            return jsonify({'error': 'Scheduled time is required'}), 400
        
        try:
            # Parse scheduled time - handle both formats: "2025-10-31T09:23:00Z" and "2025-10-31T09:23:00.000Z"
            if scheduled_time.endswith('Z'):
                # Convert Z to +00:00 for ISO format parsing
                scheduled_time_iso = scheduled_time.replace('Z', '+00:00')
            else:
                scheduled_time_iso = scheduled_time
                
            scheduled_dt = datetime.fromisoformat(scheduled_time_iso)
            
            # Compare with timezone-aware current time
            from datetime import timezone
            current_time_utc = datetime.now(timezone.utc)
            
            if scheduled_dt <= current_time_utc:
                return jsonify({
                    'error': 'Scheduled time must be in the future',
                    'provided_time': scheduled_dt.isoformat(),
                    'current_time': current_time_utc.isoformat()
                }), 400
                
            # Convert to Unix timestamp for Facebook API
            scheduled_timestamp = int(scheduled_dt.timestamp())
            
        except ValueError as ve:
            return jsonify({
                'error': 'Invalid scheduled time format',
                'provided_time': scheduled_time,
                'expected_format': 'ISO 8601 format like "2025-10-31T09:23:00.000Z"',
                'details': str(ve)
            }), 400

        # Get user's Facebook credentials
        from app.database.models.user import User
        user = User.query.get(current_user_id)
        
        # Check if user has selected a Facebook page
        if user.selected_page_id and user.selected_page_token:
            page_id = user.selected_page_id
            token = user.selected_page_token
        elif facebook_page_id:
            # Use provided page ID with user's token (if available)
            page_id = facebook_page_id
            token = user.selected_page_token if user.selected_page_token else os.getenv("FB_PAGE_ACCESS_TOKEN")
        else:
            # Fallback to environment variables
            page_id = os.getenv("FB_PAGE_ID")
            token = os.getenv("FB_PAGE_ACCESS_TOKEN")

        if not (page_id and token):
            return jsonify({
                'error': 'Facebook page not connected',
                'message': 'Please connect your Facebook page first'
            }), 400

        # Use image_data or b64_png (prefer b64_png if both provided)
        image_to_use = b64_png or image_data
        
        try:
            facebook_response = None
            
            if image_to_use:
                # Schedule post with image to Facebook
                logger.info(f"📸 Scheduling Facebook post with image for {scheduled_dt}")
                
                # Decode base64 image
                if image_to_use.startswith('data:image/'):
                    # Remove data URL prefix if present
                    image_to_use = image_to_use.split(',')[1]
                
                image_bytes = base64.b64decode(image_to_use)
                
                # Upload photo to Facebook with scheduled publish time
                url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                
                files = {
                    'source': ('scheduled_image.png', image_bytes, 'image/png')
                }
                
                params = {
                    'access_token': token,
                    'message': content,
                    'published': 'false',  # Don't publish immediately
                    'scheduled_publish_time': scheduled_timestamp
                }
                
                facebook_response = requests.post(url, files=files, data=params)
                
            else:
                # Schedule text-only post to Facebook
                logger.info(f"📝 Scheduling Facebook text post for {scheduled_dt}")
                
                url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
                
                params = {
                    'access_token': token,
                    'message': content,
                    'published': 'false',  # Don't publish immediately
                    'scheduled_publish_time': scheduled_timestamp
                }
                
                facebook_response = requests.post(url, data=params)
                
            facebook_data = facebook_response.json()
            
            if facebook_response.status_code == 200 and 'id' in facebook_data:
                # Facebook scheduling successful - now save to database
                logger.info(f"✅ Facebook post scheduled successfully: {facebook_data['id']}")
                
                # Create scheduled post record in database
                post = Post.create_post(
                    user_id=current_user_id,
                    content=content,
                    facebook_page_id=page_id,
                    scheduled_time=scheduled_dt,
                    image_data=image_to_use if image_to_use else None,
                    status='scheduled'
                )
                
                if post:
                    # Store Facebook post ID and additional metadata
                    post.platform_post_id = facebook_data['id']
                    if image_to_use:
                        post.media_urls = ['image_scheduled_with_facebook']
                    db.session.commit()
                    
                    logger.info(f"✅ Database record created for scheduled post: {post.id}")
                
                return jsonify({
                    'success': True,
                    'message': f'Post scheduled successfully for {scheduled_dt.strftime("%Y-%m-%d %H:%M:%S UTC")}',
                    'facebook_post_id': facebook_data['id'],
                    'scheduled_time': scheduled_dt.isoformat(),
                    'post': post.to_dict() if post else None,
                    'facebook_response': {
                        'post_id': facebook_data['id'],
                        'scheduled_publish_time': scheduled_timestamp
                    }
                }), 201
                
            else:
                # Facebook API error
                logger.error(f'Facebook scheduling error: {facebook_data}')
                error_message = facebook_data.get('error', {}).get('message', 'Unknown Facebook API error')
                
                return jsonify({
                    'error': 'Failed to schedule post with Facebook',
                    'details': error_message,
                    'facebook_error': facebook_data.get('error', {})
                }), 400
                
        except requests.exceptions.RequestException as e:
            logger.error(f'Facebook API request failed: {str(e)}')
            return jsonify({
                'error': 'Failed to connect to Facebook API',
                'message': 'Please check your internet connection and Facebook permissions'
            }), 500
            
        except Exception as e:
            logger.error(f'Facebook scheduling error: {str(e)}')
            
            # Fallback: Save to database only if Facebook fails
            logger.info("💾 Facebook scheduling failed, saving to database only as fallback")
            
            try:
                post = Post.create_post(
                    user_id=current_user_id,
                    content=content,
                    facebook_page_id=page_id,
                    scheduled_time=scheduled_dt,
                    image_data=image_to_use if image_to_use else None,
                    status='draft'  # Mark as draft since Facebook scheduling failed
                )
                
                if post and image_to_use:
                    post.media_urls = ['image_data_present']
                    db.session.commit()
                
                return jsonify({
                    'success': False,
                    'message': 'Facebook scheduling failed, saved as draft instead',
                    'warning': 'You will need to manually publish this post',
                    'error_details': str(e),
                    'post': post.to_dict() if post else None
                }), 202  # Accepted but not fully processed
                
            except Exception as db_error:
                logger.error(f'Database fallback also failed: {str(db_error)}')
                return jsonify({
                    'error': 'Both Facebook scheduling and database save failed',
                    'facebook_error': str(e),
                    'database_error': str(db_error)
                }), 500
        
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