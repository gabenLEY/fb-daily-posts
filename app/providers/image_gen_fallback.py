import os, base64, requests, uuid
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .watermark import apply_watermark

def _save_png(img, target_dir="static"):
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join(target_dir, filename)
    img.save(path, "PNG")
    base = os.getenv("BASE_URL", "http://localhost:8000")
    return f"{base}/static/{filename}"

def generate_placeholder_image(prompt, size="1024x1024"):
    """Generate a placeholder image when OpenAI API is unavailable"""
    width, height = map(int, size.split('x'))
    
    # Create a simple placeholder image
    img = Image.new('RGBA', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        font = ImageFont.load_default()
        text = f"Placeholder Image\n{prompt[:50]}..."
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#666666', font=font)
    except Exception:
        pass
    
    return img

def generate_image(prompt, size="1024x1024", add_watermark=True):
    # Check if we should use OpenAI or placeholder
    use_placeholder = os.getenv("USE_PLACEHOLDER_IMAGES", "false").lower() == "true"
    
    if use_placeholder:
        print("Using placeholder image due to configuration")
        img = generate_placeholder_image(prompt, size)
    else:
        try:
            key = os.getenv("OPENAI_API_KEY")
            url = "https://api.openai.com/v1/images/generations"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            body = {"prompt": prompt, "size": size, "n": 1, "response_format": "b64_json"}
            r = requests.post(url, headers=headers, json=body, timeout=120)
            r.raise_for_status()
            b64 = r.json()["data"][0]["b64_json"]
            img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                # Check if it's a billing issue
                error_data = e.response.json()
                if error_data.get("error", {}).get("code") == "billing_hard_limit_reached":
                    print("OpenAI billing limit reached, using placeholder image")
                    img = generate_placeholder_image(prompt, size)
                else:
                    raise
            else:
                raise
        except Exception as e:
            print(f"Error with OpenAI API, using placeholder: {e}")
            img = generate_placeholder_image(prompt, size)

    if add_watermark:
        logo_path = os.getenv("BRAND_LOGO_PATH")
        logo_url  = os.getenv("BRAND_LOGO_URL")
        img = apply_watermark(img, logo_path=logo_path, logo_url=logo_url)

    image_url = _save_png(img)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    b64_png = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
    return {"imageUrl": image_url, "b64_png": b64_png}