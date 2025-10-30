"""
Test script to check OpenAI DALL-E API response structure
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI DALL-E API and show response structure"""
    
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    # Test with dall-e-3 model
    body = {
        "model": "dall-e-3",
        "prompt": "A simple test image of a red apple",
        "size": "1024x1024",
        "n": 1,
        "response_format": "url"
    }

    print("🚀 Testing OpenAI DALL-E API...")
    print(f"📝 Request body: {json.dumps(body, indent=2)}")
    
    try:
        r = requests.post(url, headers=headers, json=body, timeout=120)
        
        print(f"📊 Response status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"❌ API Error: {r.text}")
            return
        
        data = r.json()
        print("✅ API Response:")
        print(json.dumps(data, indent=2))
        
        # Check response structure
        if "data" in data and data["data"]:
            first_image = data["data"][0]
            print(f"\n🔍 Available keys in image data: {list(first_image.keys())}")
            
            for key, value in first_image.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:50]}... (truncated)")
                else:
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_openai_api()