import requests, base64
from PIL import Image
from io import BytesIO

def test_fixed_endpoint():
    """Test the fixed Facebook endpoint that should no longer get 400 error"""
    
    # Create a simple test image in base64 format
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    b64_png = f"data:image/png;base64,{img_data}"
    
    # Test data
    test_data = {
        "b64_png": b64_png,
        "caption": "Test post from fixed API - should save as draft",
        "publish_now": False,  # This was causing the scheduling error
        "time": "09:00"
    }
    
    print("Testing fixed Facebook endpoint...")
    print(f"Data: publish_now={test_data['publish_now']}, time={test_data['time']}")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/facebook/publish_binary',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS: The 400 error has been fixed!")
        elif response.status_code == 400:
            print("❌ Still getting 400 error")
        else:
            print(f"ℹ️  Got {response.status_code} - check response for details")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_fixed_endpoint()