import os, requests, base64
from dotenv import load_dotenv

def mock_facebook_publish(data):
    """Mock Facebook publish for testing when credentials aren't working"""
    print("MOCK: Facebook publish called with:")
    print(f"  - Caption: {data.get('caption', '')[:50]}...")
    print(f"  - Has image: {'b64_png' in data}")
    print(f"  - Publish now: {data.get('publish_now', False)}")
    
    return {
        "success": True,
        "message": "Mock Facebook publish (no actual posting)",
        "mock_post_id": "mock_123456789",
        "status": "This is a test response - not posted to Facebook"
    }, 200

# Test this mock function
if __name__ == "__main__":
    test_data = {
        "caption": "Test post from my app",
        "b64_png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "publish_now": False,
        "time": "09:00"
    }
    
    result, status = mock_facebook_publish(test_data)
    print(f"\nResult ({status}): {result}")