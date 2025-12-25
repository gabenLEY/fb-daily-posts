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
    """Generate AI image with dynamic watermark support"""
    logger.info("🖼️  POST /api/generate-image endpoint called")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        size = data.get('size', '1024x1024')
        
        # Dynamic watermark parameters from user
        logo_path = data.get('logo_path')  # User-provided logo path
        logo_url = data.get('logo_url')  # User-provided logo URL
        footer_text = data.get('footer_text')  # User-provided footer text
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        logger.info(f"✅ Generating image for prompt: '{prompt[:50]}...'")
        
        # Generate image with dynamic watermark
        result = generate_image(
            prompt, 
            size=size, 
            add_watermark=True,
            logo_path=logo_path,
            logo_url=logo_url,
            footer_text=footer_text
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f'💥 Failed to generate image: {str(e)}')
        import traceback
        logger.error(f'💥 Traceback: {traceback.format_exc()}')
        return jsonify({'error': 'Failed to generate image'}), 500

def _format_facebook_text(text):
    """
    Format text for Facebook posts with support for:
    - Bold: **text** or *text*
    - Italic: _text_
    - Line breaks: \n
    - Links: [text](url)
    Facebook supports basic formatting, so we'll convert markdown-like syntax
    """
    import re
    formatted = text
    
    # Convert **bold** to Facebook format (Facebook doesn't support markdown, but we can use Unicode)
    # Facebook supports some formatting, but for simplicity, we'll keep it as-is
    # and let Facebook handle natural formatting
    
    # Ensure line breaks are preserved
    formatted = formatted.replace('\\n', '\n')
    
    return formatted

@social_bp.route('/publish-facebook', methods=['POST'])
@auth_required
def publish_to_facebook():
    """Publish post to Facebook - Always saves to database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_user_id = request.user_id
        post_id = data.get('post_id')
        b64_png = data.get('b64_png')
        caption = data.get('caption', '')
        publish_now = bool(data.get('publish_now', True))
        image_url = data.get('image_url')
        title = data.get('title')
        
        # Get post if post_id provided
        post = None
        if post_id:
            post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
            if not post:
                return jsonify({'error': 'Post not found or permission denied'}), 404
            
            # Use post data if not provided in request
            if not caption:
                caption = post.caption
            if not b64_png and post.image_data:
                b64_png = post.image_data
            if not image_url and post.image_url:
                image_url = post.image_url
        
        if not b64_png:
            return jsonify({'error': 'Image data is required'}), 400
        
        if not caption:
            return jsonify({'error': 'Caption is required'}), 400
        
        # Format caption text for Facebook
        formatted_caption = _format_facebook_text(caption)
        
        # Get user's Facebook credentials
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
            image_data = base64.b64decode(b64_png.split(',')[-1] if ',' in b64_png else b64_png)
            
            # Upload photo to Facebook
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            
            files = {
                'source': ('image.png', image_data, 'image/png')
            }
            
            params = {
                'access_token': token,
                'message': formatted_caption,  # Use formatted text
                'published': 'true' if publish_now else 'false'
            }
            
            response = requests.post(url, files=files, data=params)
            response_data = response.json()
            
            if response.status_code == 200 and 'id' in response_data:
                facebook_post_id = response_data['id']
                
                # Always save/update post in database
                if post:
                    # Update existing post
                    post.status = 'published' if publish_now else 'scheduled'
                    post.published_at = datetime.utcnow() if publish_now else None
                    post.facebook_post_id = facebook_post_id
                    post.caption = caption  # Store original caption
                    if image_url:
                        post.image_url = image_url
                    if b64_png:
                        post.image_data = b64_png
                else:
                    # Create new post record
                    post = Post(
                        user_id=current_user_id,
                        title=title,
                        caption=caption,
                        image_url=image_url,
                        image_data=b64_png,
                        facebook_post_id=facebook_post_id,
                        status='published' if publish_now else 'scheduled',
                        published_at=datetime.utcnow() if publish_now else None
                    )
                    db.session.add(post)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Post published successfully' if publish_now else 'Post scheduled successfully',
                    'facebook_post_id': facebook_post_id,
                    'post_id': post.id,
                    'post_url': f"https://www.facebook.com/{facebook_post_id}",
                    'post': post.to_dict()
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
        db.session.rollback()
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
        caption = data.get('caption') or data.get('content', '').strip()  # Support both
        image_data = data.get('image_data')  # base64 encoded image
        image_url = data.get('image_url')
        title = data.get('title')
        scheduled_time = data.get('scheduled_time')
        
        if not caption:
            return jsonify({'error': 'Caption is required'}), 400
        
        # Parse scheduled_time if provided
        scheduled_dt = None
        if scheduled_time:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                if scheduled_dt.tzinfo:
                    scheduled_dt = scheduled_dt.replace(tzinfo=None)
            except ValueError:
                pass
        
        # Create draft post
        post = Post.create_post(
            user_id=current_user_id,
            caption=caption,
            title=title,
            image_url=image_url,
            image_data=image_data,
            scheduled_time=scheduled_dt,
            status='draft'
        )
        
        if not post:
            return jsonify({'error': 'Failed to save draft'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Draft saved successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Save draft failed: {str(e)}')
        db.session.rollback()
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
        caption = data.get('caption') or data.get('content', '').strip()  # Support both
        scheduled_time = data.get('scheduled_time')
        image_data = data.get('image_data')
        image_url = data.get('image_url')
        title = data.get('title')
        
        if not caption:
            return jsonify({'error': 'Caption is required'}), 400
        
        if not scheduled_time:
            return jsonify({'error': 'Scheduled time is required'}), 400
        
        try:
            # Parse scheduled time
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            if scheduled_dt.tzinfo:
                scheduled_dt = scheduled_dt.replace(tzinfo=None)
            if scheduled_dt <= datetime.utcnow():
                return jsonify({'error': 'Scheduled time must be in the future'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid scheduled time format'}), 400
        
        # Create scheduled post
        post = Post.create_post(
            user_id=current_user_id,
            caption=caption,
            title=title,
            image_url=image_url,
            image_data=image_data,
            scheduled_time=scheduled_dt,
            status='scheduled'
        )
        
        if not post:
            return jsonify({'error': 'Failed to schedule post'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Post scheduled successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Schedule post failed: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Failed to schedule post'}), 500

def _generate_content_with_business_context(business_context, day_number, style, total_posts):
    """
    Generate content based on business context and day number.
    Uses AI to create relevant topics and content for each day.
    """
    try:
        # Create a context-aware topic that varies by day
        # This helps generate diverse content throughout the period
        topic_variations = [
            f"{business_context} - Tips & Insights",
            f"{business_context} - Special Offers",
            f"{business_context} - Success Stories",
            f"{business_context} - Product Highlights",
            f"{business_context} - Community Spotlight",
            f"{business_context} - Behind the Scenes",
            f"{business_context} - Educational Content",
            f"{business_context} - Customer Testimonials",
            f"{business_context} - Industry News",
            f"{business_context} - How-To Guides"
        ]
        
        # Cycle through variations based on post number
        topic_index = (day_number - 1) % len(topic_variations)
        topic = topic_variations[topic_index]
        
        # Use refine_prompt_and_captions with the topic
        result = refine_prompt_and_captions(
            topic=topic,
            style=style
        )
        
        return {
            'topic': topic,
            'prompt': result.get('prompt', f"A {style} related to {business_context}"),
            'caption': result.get('caption_en') or f"Check out our {business_context} content!"
        }
    except Exception as e:
        logger.error(f'Error generating content with business context: {str(e)}')
        # Fallback
        return {
            'topic': f"{business_context} - Post {day_number}",
            'prompt': f"A {style} related to {business_context}",
            'caption': f"Check out our {business_context} content for post {day_number}!"
        }

@social_bp.route('/auto-generate-posts', methods=['POST'])
@auth_required
def auto_generate_posts():
    """
    Auto-generate posts with flexible duration and posting frequency.
    Supports: daily, every 3 days, every 5 days, etc.
    Can auto-generate content based on business context or use provided topics.
    """
    try:
        data = request.get_json() or {}
        current_user_id = request.user_id
        
        # Get parameters
        business_context = data.get('business_context', '').strip()  # Main business/page context
        style = data.get('style', 'clean product shot').strip()
        start_date = data.get('start_date')  # ISO format date string
        default_time = data.get('default_time', '09:00')  # Default publish time
        logo_path = data.get('logo_path')
        logo_url = data.get('logo_url')
        footer_text = data.get('footer_text')
        
        # Duration parameters
        duration_type = data.get('duration_type', 'days')  # 'days', 'weeks', 'months'
        duration_value = data.get('duration', 7)  # Number of days/weeks/months
        
        # Posting frequency
        posting_frequency = data.get('posting_frequency', 1)  # Every N days (1 = daily, 3 = every 3 days, etc.)
        
        # Daily topics (optional - if provided, use these; otherwise auto-generate)
        daily_topics = data.get('daily_topics', [])  # Array of topics for each post day
        
        if not business_context:
            return jsonify({'error': 'Business context is required for auto-generation'}), 400
        
        # Parse start date (default to today)
        from datetime import timedelta
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                # Remove timezone info for local calculation
                if start_dt.tzinfo:
                    start_dt = start_dt.replace(tzinfo=None)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
        else:
            start_dt = datetime.utcnow()
        
        # Calculate total duration in days
        if duration_type == 'weeks':
            total_days = duration_value * 7
        elif duration_type == 'months':
            total_days = duration_value * 30  # Approximate
        else:
            total_days = duration_value
        
        # Calculate how many posts we'll generate based on frequency
        post_days = []
        current_day = 0
        post_number = 0
        
        while current_day < total_days:
            post_days.append({
                'day_offset': current_day,
                'post_number': post_number + 1
            })
            current_day += posting_frequency
            post_number += 1
        
        # Parse default time
        time_parts = default_time.split(':')
        default_hour = int(time_parts[0]) if len(time_parts) > 0 else 9
        default_minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        generated_posts = []
        errors = []
        
        for post_info in post_days:
            try:
                day_offset = post_info['day_offset']
                post_num = post_info['post_number']
                
                # Calculate scheduled time for this post
                scheduled_time = start_dt + timedelta(days=day_offset)
                scheduled_time = scheduled_time.replace(
                    hour=default_hour,
                    minute=default_minute,
                    second=0,
                    microsecond=0
                )
                
                # Get topic for this post
                if daily_topics and len(daily_topics) > post_num - 1:
                    # Use provided topic
                    topic = daily_topics[post_num - 1]
                    prompt_result = refine_prompt_and_captions(
                        topic=f"{business_context}: {topic}",
                        style=style
                    )
                    prompt = prompt_result.get('prompt', f"A {style} of {topic}")
                    caption = prompt_result.get('caption_en') or (prompt_result.get('captions', [f"Check out this {topic}!"])[0] if isinstance(prompt_result.get('captions'), list) else f"Amazing {topic} content!")
                else:
                    # Auto-generate content based on business context
                    content = _generate_content_with_business_context(business_context, post_num, style, len(post_days))
                    topic = content['topic']
                    prompt = content['prompt']
                    caption = content['caption']
                
                # Generate image
                image_result = generate_image(
                    prompt=prompt,
                    size="1024x1792",  # Flyer size
                    add_watermark=True,
                    logo_path=logo_path,
                    logo_url=logo_url,
                    footer_text=footer_text
                )
                
                # Create post in database with scheduled status
                post = Post(
                    user_id=current_user_id,
                    title=f"{business_context} - Post {post_num}",
                    caption=caption,
                    image_url=image_result.get('imageUrl'),
                    image_data=image_result.get('b64_png'),
                    status='scheduled',
                    scheduled_time=scheduled_time
                )
                
                db.session.add(post)
                db.session.flush()  # Get the post ID
                
                generated_posts.append({
                    'post_id': post.id,
                    'post_number': post_num,
                    'day_offset': day_offset,
                    'scheduled_time': scheduled_time.isoformat(),
                    'topic': topic,
                    'caption': caption,
                    'image_url': image_result.get('imageUrl')
                })
                
            except Exception as e:
                logger.error(f'Error generating post {post_num}: {str(e)}')
                errors.append(f"Post {post_num}: {str(e)}")
                continue
        
        # Commit all posts
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'error': 'Failed to save posts to database',
                'details': str(e)
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_posts)} posts over {total_days} days',
            'posts': generated_posts,
            'errors': errors if errors else None,
            'total_generated': len(generated_posts),
            'total_errors': len(errors),
            'duration_days': total_days,
            'posting_frequency': f'Every {posting_frequency} day(s)',
            'total_posts': len(generated_posts)
        }), 201
        
    except Exception as e:
        logger.error(f'Auto-generate posts failed: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Failed to auto-generate posts'}), 500

# Keep old endpoint for backward compatibility
@social_bp.route('/auto-generate-weekly-posts', methods=['POST'])
@auth_required
def auto_generate_weekly_posts():
    """Auto-generate 7 posts for the week (backward compatibility)"""
    data = request.get_json() or {}
    # Convert to new format
    data['duration_type'] = 'weeks'
    data['duration'] = 1
    data['posting_frequency'] = 1
    if 'business_context' not in data and 'topic' in data:
        data['business_context'] = data.get('topic', '')
    return auto_generate_posts()

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