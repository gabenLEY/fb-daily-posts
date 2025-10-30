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

def generate_image(prompt, size="1024x1024", add_watermark=True):
    key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-image-1",      # ✅ correct model name for DALL-E 3
        "prompt": prompt,
        "size": size,             # "1024x1024" | "1024x1792" | "1792x1024" for DALL-E 3
        "n": 1,
        #"response_format": "url"  # or "b64_json" - let's try URL first
    }

    # Use reasonable timeout - OpenAI can take 20-40 seconds
    timeout = int(os.getenv('IMAGE_GENERATION_TIMEOUT', '35'))  # 35 seconds
    
    try:
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
    except requests.exceptions.Timeout:
        # If timeout, fall back to a simpler/faster model or return a placeholder
        print(f"⚠️ OpenAI timeout after {timeout}s, trying fallback...")
        
        # Try with a simpler prompt or return a placeholder
        fallback_body = {
            "model": "dall-e-2",  # Faster model
            "prompt": prompt[:100],  # Shorter prompt
            "size": "1024x1024",
            "n": 1
        }
        
        try:
            r = requests.post(url, headers=headers, json=fallback_body, timeout=20)
        except:
            # Ultimate fallback - return placeholder
            print("⚠️ All OpenAI attempts failed, using placeholder")
            return {
                'image_url': f'https://via.placeholder.com/{size.replace("x", "x")}/cccccc/666666?text=Image+Generation+Timeout',
                'b64_image': None,
                'fallback': True
            }

    if r.status_code != 200:
        print("⚠️ OpenAI error:", r.text)
        r.raise_for_status()

    data = r.json()
   # print("✅ OpenAI image generation response:", data)
    
    # Check if response has expected structure
    if "data" not in data or not data["data"]:
        raise Exception(f"Invalid OpenAI response structure: {data}")
    
    # Check what keys are available in the response
    first_image = data["data"][0]
    #print("🔍 Available keys in image data:", list(first_image.keys()))
    
    # Try different possible keys for the image URL
    image_url_from_openai = None
    possible_keys = ["url", "image_url", "revised_prompt", "b64_json"]
    
    for key in possible_keys:
        if key in first_image:
            if key == "b64_json":
                # If we get base64 data, we need to handle it differently
                print(f"📝 Found base64 data instead of URL")
                break
            else:
                image_url_from_openai = first_image[key]
                print(f"📝 Found image URL using key: {key}")
                break
    
    if not image_url_from_openai and "b64_json" not in first_image:
        raise Exception(f"No image URL found in OpenAI response. Available keys: {list(first_image.keys())}")

    # 👉 Handle both URL and base64 responses
    if "b64_json" in first_image:
        # Handle base64 response
        print("📥 Processing base64 image data")
        b64_data = first_image["b64_json"]
        img_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        image_url_from_openai = None  # No external URL for base64
    else:
        # Handle URL response
        print(f"📥 Downloading image from URL: {image_url_from_openai}")
        img_resp = requests.get(image_url_from_openai, timeout=120)
        img_resp.raise_for_status()
        img = Image.open(BytesIO(img_resp.content)).convert("RGBA")

    if add_watermark:
        logo_path = os.getenv("BRAND_LOGO_PATH")
        logo_url  = os.getenv("BRAND_LOGO_URL")
        img = apply_watermark(img, logo_path=logo_path, logo_url=logo_url)

    # your own save logic
    image_url = _save_png(img)

    # if you still want to return base64 to your frontend:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    b64_png = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {
        "imageUrl": image_url,                    # your local/s3 path
        "openaiImageUrl": image_url_from_openai or "generated_from_base64",  # original from OpenAI or indicator
        "b64_png": b64_png,
        "prompt": prompt,
        "size": size
    }

