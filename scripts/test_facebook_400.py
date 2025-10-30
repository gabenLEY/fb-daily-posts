import os, requests, base64
from dotenv import load_dotenv

load_dotenv()

def test_facebook_publish_binary():
    """Test the exact same call that's failing with 400 error"""
    
    page_id = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print("Testing Facebook publish_binary endpoint...")
    print(f"Page ID: {page_id}")
    print(f"Token: {token[:20]}...")
    
    if not (page_id and token):
        print("❌ Missing Facebook credentials")
        return
    
    # Create a simple test image in base64 format
    from PIL import Image
    from io import BytesIO
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    b64_png = f"data:image/png;base64,{img_data}"
    
    # Test data matching what the endpoint expects
    test_data = {
        "b64_png": b64_png,
        "caption": "Test post from API",
        "publish_now": False,
        "time": "09:00"
    }
    
    # Test the Facebook API directly (same as the endpoint does)
    print("\n1. Testing direct Facebook API call...")
    try:
        raw = base64.b64decode(b64_png.split(",")[-1])
        files = {"source": ("image.png", raw, "image/png")}
        data_form = {"caption": test_data["caption"], "access_token": token}
        
        # Add scheduling parameters
        from utils.schedule import unix_for_today_or_tomorrow
        if not test_data["publish_now"]:
            data_form.update({
                "published": "false", 
                "unpublished_content_type": "SCHEDULED",
                "scheduled_publish_time": str(unix_for_today_or_tomorrow(test_data["time"])),
            })
        
        fb_url = f"https://graph.facebook.com/v24.0/{page_id}/photos"
        print(f"URL: {fb_url}")
        print(f"Form data: {data_form}")
        
        r = requests.post(fb_url, data=data_form, files=files, timeout=120)
        print(f"Response status: {r.status_code}")
        print(f"Response: {r.text}")
        
    except Exception as e:
        print(f"Direct API error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the local endpoint
    print("\n2. Testing local API endpoint...")
    try:
        response = requests.post(
            'http://localhost:8000/api/facebook/publish_binary',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"Local endpoint status: {response.status_code}")
        print(f"Local endpoint response: {response.text}")
        
    except Exception as e:
        print(f"Local endpoint error: {e}")

if __name__ == "__main__":
    test_facebook_publish_binary()