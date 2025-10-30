import os, requests, base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

def test_facebook_with_detailed_logging():
    """Test Facebook endpoint with detailed logging to identify the 403 error"""
    
    print("=== Testing Facebook Endpoint with Detailed Logging ===")
    
    # Create test image
    img = Image.new('RGB', (100, 100), color='green')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    b64_png = f"data:image/png;base64,{img_data}"
    
    test_cases = [
        {
            "name": "Test Case 1: Publish Now = True",
            "data": {
                "b64_png": b64_png,
                "caption": "Test immediate publish",
                "publish_now": True
            }
        },
        {
            "name": "Test Case 2: Publish Now = False (Draft)",
            "data": {
                "b64_png": b64_png,
                "caption": "Test draft save",
                "publish_now": False,
                "time": "09:00"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Data: {test_case['data']}")
        
        try:
            # Test with explicit headers and timeout
            response = requests.post(
                'http://localhost:8000/api/facebook/publish_binary',
                json=test_case['data'],
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'TestClient/1.0'
                },
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 403:
                print("❌ 403 FORBIDDEN - Authentication/Permission issue")
            elif response.status_code == 400:
                print("❌ 400 BAD REQUEST - Invalid parameters")
            elif response.status_code == 200:
                print("✅ SUCCESS")
            else:
                print(f"ℹ️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request Exception: {type(e).__name__}: {e}")
    
    # Test direct Facebook API to compare
    print(f"\n--- Direct Facebook API Test ---")
    try:
        page_id = os.getenv("FB_PAGE_ID")
        token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        
        raw = base64.b64decode(b64_png.split(",")[-1])
        files = {"source": ("test.png", raw, "image/png")}
        data_form = {"caption": "Direct API test", "access_token": token, "published": "false"}
        
        fb_url = f"https://graph.facebook.com/v24.0/{page_id}/photos"
        r = requests.post(fb_url, data=data_form, files=files, timeout=120)
        
        print(f"Direct FB API Status: {r.status_code}")
        print(f"Direct FB API Response: {r.text}")
        
    except Exception as e:
        print(f"Direct FB API Error: {e}")

if __name__ == "__main__":
    test_facebook_with_detailed_logging()