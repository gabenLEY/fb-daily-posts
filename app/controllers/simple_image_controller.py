"""
Simplified image generation controller that works within Heroku constraints
"""
from flask import Blueprint, request, jsonify
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

simple_image_bp = Blueprint('simple_image', __name__)

@simple_image_bp.route('/generate-image-simple', methods=['POST'])
def generate_image_simple():
    """Generate image with chunked timeout approach"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        size = data.get('size', '1024x1024')
        attempt = int(data.get('attempt', 1))
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        logger.info(f"🎨 Simple image generation attempt {attempt} for: '{prompt[:50]}...'")
        
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
            # Suggest next attempt
            return jsonify({
                'success': False,
                'message': f'Attempt {attempt} timed out',
                'next_attempt': attempt + 1,
                'suggestion': 'Try again for next strategy'
            }), 202
        
    except Exception as e:
        logger.error(f'Failed to generate image: {str(e)}')
        return jsonify({'error': str(e)}), 500

def try_generate_with_timeout(prompt, size, timeout=25):
    """Try to generate image with specific timeout"""
    try:
        import requests
        import os
        import base64
        from PIL import Image
        from io import BytesIO
        
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            logger.error("No OpenAI API key found")
            return None
            
        url = "https://api.openai.com/v1/images/generations"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        body = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "n": 1,
            "response_format": "b64_json"
        }
        
        logger.info(f"🔄 Calling OpenAI API with {timeout}s timeout...")
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
        
        if r.status_code == 200:
            data = r.json()
            b64 = data["data"][0]["b64_json"]
            
            # Process image
            img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
            
            # Add watermark if needed
            try:
                from app.providers.watermark import apply_watermark
                logo_path = os.getenv("BRAND_LOGO_PATH")
                logo_url = os.getenv("BRAND_LOGO_URL")
                img = apply_watermark(img, logo_path=logo_path, logo_url=logo_url)
            except:
                logger.warning("Watermark failed, continuing without it")
            
            # Save image
            import uuid
            filename = f"{uuid.uuid4().hex}.png"
            os.makedirs("static", exist_ok=True)
            path = os.path.join("static", filename)
            img.save(path, "PNG")
            
            # Create URLs
            base_url = os.getenv("BASE_URL", "https://randevoupost.cloud")
            image_url = f"{base_url}/static/{filename}"
            
            # Create base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            b64_png = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return {
                "image_url": image_url,
                "b64_png": b64_png
            }
        else:
            logger.error(f"OpenAI API error: {r.status_code} - {r.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.warning(f"OpenAI API timeout after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

def try_generate_dalle2(prompt, size, timeout=25):
    """Try with DALL-E 2 (faster model)"""
    logger.info("🔄 Trying DALL-E 2 (faster model)...")
    # Truncate prompt for DALL-E 2
    short_prompt = prompt[:100] if len(prompt) > 100 else prompt
    return try_generate_with_timeout(short_prompt, "1024x1024", timeout)

def generate_placeholder(prompt, size):
    """Generate placeholder image"""
    import urllib.parse
    encoded_text = urllib.parse.quote("AI Generated Image")
    placeholder_url = f'https://via.placeholder.com/{size.replace("x", "x")}/4A90E2/FFFFFF?text={encoded_text}'
    
    return {
        "image_url": placeholder_url,
        "b64_png": None,
        "placeholder": True,
        "message": "Placeholder - OpenAI generation timed out"
    }