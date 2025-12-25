import os, base64, requests, uuid
from PIL import Image
from io import BytesIO
from app.providers.watermark import apply_watermark

def _save_png(img, target_dir="static"):
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join(target_dir, filename)
    img.save(path, "PNG")
    base = os.getenv("BASE_URL", "http://localhost:8000")
    return f"{base}/static/{filename}"

def generate_image(prompt, size="1024x1024", add_watermark=True, logo_path=None, logo_url=None, footer_text=None):
    """
    Generate professional images and flyers using GPT-Image-1.5 (newest model).
    Uses base64 response format to avoid Heroku timeout issues with URL downloads.
    Optimized for flyer creation with professional quality.
    
    Args:
        prompt: Image generation prompt
        size: Image size (defaults to 1024x1792 for flyers)
        add_watermark: Whether to add watermark
        logo_path: Path to logo file (dynamic from user)
        logo_url: URL to logo (dynamic from user)
        footer_text: Footer text for watermark (dynamic from user)
    """
    key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    # Use GPT-Image-1.5 (newest model) for professional images and flyers
    # Optimize size for flyers: 1024x1792 (portrait) or 1792x1024 (landscape)
    if size == "1024x1024":
        size = "1024x1792"  # Default to portrait flyer size
    
    body = {
        "model": "gpt-image-1.5",  # Newest model (GPT-Image-1.5) for professional images and flyers
        "prompt": prompt,
        "size": size,  # "1024x1024" | "1024x1792" | "1792x1024"
        "n": 1,
        "response_format": "b64_json",  # Use base64 to skip URL download (avoids Heroku timeout)
        "quality": "hd",  # High quality for professional images
        "style": "vivid"  # Vivid style for professional flyers
    }

    # Use longer timeout for professional image generation (up to 3 minutes)
    timeout = int(os.getenv('IMAGE_GENERATION_TIMEOUT', '180'))  # 3 minutes (180 seconds)
    
    try:
        print(f"🎨 Generating professional image/flyer with GPT-Image-1.5 (size: {size})...")
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"⚠️ OpenAI timeout after {timeout}s - image generation takes time")
        raise Exception(f"Image generation timed out after {timeout} seconds. Please try again.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ OpenAI API error: {e}")
        raise

    data = r.json()
    
    # Check if response has expected structure
    if "data" not in data or not data["data"]:
        raise Exception(f"Invalid OpenAI response structure: {data}")
    
    # Get the first image from response
    first_image = data["data"][0]
    
    # Process base64 image data directly (skip URL download to avoid timeout)
    if "b64_json" not in first_image:
        raise Exception(f"No base64 image data found in OpenAI response. Available keys: {list(first_image.keys())}")

    # Handle base64 response (faster, avoids URL download timeout on Heroku)
    print("📥 Processing base64 image data (skipping URL download for Heroku compatibility)")
    b64_data = first_image["b64_json"]
    img_data = base64.b64decode(b64_data)
    img = Image.open(BytesIO(img_data)).convert("RGBA")

    # Apply watermark with dynamic logo from user (if provided)
    if add_watermark:
        # Use user-provided logo if available, otherwise fall back to env vars
        user_logo_path = logo_path or os.getenv("BRAND_LOGO_PATH")
        user_logo_url = logo_url or os.getenv("BRAND_LOGO_URL")
        user_footer_text = footer_text or os.getenv("BRAND_FOOTER", "ChatRefill • Top-up worldwide")
        img = apply_watermark(img, logo_path=user_logo_path, logo_url=user_logo_url, footer_text=user_footer_text)

    # your own save logic
    image_url = _save_png(img)

    # if you still want to return base64 to your frontend:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    b64_png = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Get revised prompt if available (GPT-Image-1.5 provides this)
    revised_prompt = first_image.get("revised_prompt", prompt)
    
    return {
        "imageUrl": image_url,  # Local saved image path
        "b64_png": b64_png,  # Base64 encoded image for immediate use
        "prompt": prompt,  # Original prompt
        "revised_prompt": revised_prompt,  # GPT-Image-1.5's improved prompt
        "size": size,
        "model": "gpt-image-1.5"  # Model used for generation
    }

