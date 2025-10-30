import os, requests, base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

def test_modern_facebook_api():
    """Test the modern Facebook API approach"""
    
    page_id = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print("=== Testing Modern Facebook Feed API ===")
    
    # Create test image
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    raw_data = buffer.getvalue()
    
    # Test the feed endpoint directly
    fb_url = f"https://graph.facebook.com/v24.0/{page_id}/feed"
    
    feed_data = {
        "message": "Test post from modern API - should be draft",
        "access_token": token,
        "published": "false"  # Save as draft
    }
    
    feed_files = {"source": ("test.png", raw_data, "image/png")}
    
    print(f"URL: {fb_url}")
    print(f"Data: {feed_data}")
    
    try:
        r = requests.post(fb_url, data=feed_data, files=feed_files, timeout=120)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("✅ SUCCESS: Modern API works!")
        else:
            print(f"❌ Still getting error: {r.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_modern_facebook_api()