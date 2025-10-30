import os, requests, base64
from dotenv import load_dotenv
from utils.schedule import unix_for_today_or_tomorrow

load_dotenv()

# Test Facebook API to see what's causing the 403 error
def test_facebook_api():
    print("Testing Facebook API...")
    
    page_id = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print(f"FB_PAGE_ID: {page_id}")
    print(f"FB_PAGE_ACCESS_TOKEN: {token[:20] if token else None}...")
    
    if not (page_id and token):
        print("ERROR: Facebook credentials missing!")
        return
    
    # Test 1: Check if token is valid by getting page info
    print("\n1. Testing page access...")
    try:
        page_url = f"https://graph.facebook.com/v24.0/{page_id}?access_token={token}"
        r = requests.get(page_url, timeout=30)
        print(f"Page info status: {r.status_code}")
        print(f"Page info response: {r.text}")
    except Exception as e:
        print(f"Page info error: {e}")
    
    # Test 2: Check token permissions
    print("\n2. Testing token permissions...")
    try:
        perms_url = f"https://graph.facebook.com/v24.0/me/permissions?access_token={token}"
        r = requests.get(perms_url, timeout=30)
        print(f"Permissions status: {r.status_code}")
        print(f"Permissions response: {r.text}")
    except Exception as e:
        print(f"Permissions error: {e}")
    
    # Test 3: Try a simple photo upload
    print("\n3. Testing photo upload...")
    try:
        # Create a simple test image
        from PIL import Image
        from io import BytesIO
        
        # Create a simple 100x100 red image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        files = {"source": ("test.png", buffer.getvalue(), "image/png")}
        data_form = {
            "caption": "Test post from API",
            "access_token": token,
            "published": "false"  # Don't actually publish
        }
        
        fb_url = f"https://graph.facebook.com/v24.0/{page_id}/photos"
        r = requests.post(fb_url, data=data_form, files=files, timeout=120)
        print(f"Photo upload status: {r.status_code}")
        print(f"Photo upload response: {r.text}")
        
    except Exception as e:
        print(f"Photo upload error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_facebook_api()