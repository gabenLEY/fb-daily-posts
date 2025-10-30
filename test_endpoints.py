"""
Test the /api/generate-image endpoint with proper data
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_generate_image():
    print("🧪 Testing /api/generate-image endpoint\n")
    
    # Test 1: Empty request (should return 400)
    print("1. Testing empty request:")
    try:
        response = requests.post(f"{BASE_URL}/api/generate-image", json={})
        print(f"   Empty data -> {response.status_code}")
        if response.status_code == 400:
            print(f"   Error message: {response.json()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Missing prompt (should return 400)
    print("\n2. Testing missing prompt:")
    try:
        response = requests.post(f"{BASE_URL}/api/generate-image", json={"size": "1024x1024"})
        print(f"   Missing prompt -> {response.status_code}")
        if response.status_code == 400:
            print(f"   Error message: {response.json()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Valid request (should return 200 or generate image)
    print("\n3. Testing valid request:")
    try:
        valid_data = {
            "prompt": "A beautiful sunset over mountains",
            "size": "1024x1024"
        }
        response = requests.post(f"{BASE_URL}/api/generate-image", json=valid_data)
        print(f"   Valid data -> {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            if 'data' in result:
                print(f"   Generated image info: {result['data']}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Test the /api/prompt endpoint too
    print("\n4. Testing /api/prompt endpoint:")
    try:
        valid_data = {
            "topic": "coffee shop",
            "style": "modern minimalist"
        }
        response = requests.post(f"{BASE_URL}/api/prompt", json=valid_data)
        print(f"   Valid data -> {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            if 'data' in result:
                print(f"   Generated prompt: {result['data']}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    test_generate_image()