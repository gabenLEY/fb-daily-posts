import os, requests, base64
from dotenv import load_dotenv

load_dotenv()

def test_facebook_token_permissions():
    """Test if the Facebook token has the right permissions"""
    
    page_id = os.getenv("FB_PAGE_ID")  # 885186207348933
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print("=== Testing Facebook Token Permissions ===")
    print(f"Page ID: {page_id}")
    print(f"Token: {token[:20]}...")
    
    # Test 1: Can we access the page?
    print("\n1. Testing page access...")
    try:
        url = f"https://graph.facebook.com/v24.0/{page_id}?access_token={token}"
        r = requests.get(url, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Page accessible: {data.get('name', 'Unknown')}")
        else:
            print("❌ Cannot access page")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: What permissions do we have?
    print("\n2. Testing token permissions...")
    try:
        url = f"https://graph.facebook.com/v24.0/me/permissions?access_token={token}"
        r = requests.get(url, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            perms = r.json()
            granted_perms = [p['permission'] for p in perms.get('data', []) if p.get('status') == 'granted']
            print(f"✅ Granted permissions: {granted_perms}")
        else:
            print("❌ Cannot get permissions")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Can we post to the page?
    print("\n3. Testing page posting capability...")
    try:
        # Create tiny test image
        from PIL import Image
        from io import BytesIO
        
        img = Image.new('RGB', (50, 50), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        files = {"source": ("test.png", buffer.getvalue(), "image/png")}
        data_form = {
            "caption": "API Test - should be draft",
            "access_token": token,
            "published": "false"  # Save as draft
        }
        
        url = f"https://graph.facebook.com/v24.0/{page_id}/photos"
        r = requests.post(url, data=data_form, files=files, timeout=120)
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("✅ Can post to page!")
        elif r.status_code == 403:
            print("❌ 403: Permission denied - token lacks posting permissions")
        elif r.status_code == 400:
            print("❌ 400: Bad request - check parameters")
        else:
            print(f"❌ Unexpected status: {r.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_facebook_token_permissions()