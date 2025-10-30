#!/usr/bin/env python3
"""
Test immediate Facebook publishing (publish_now=True)
"""

import requests
import json

# Test data
test_data = {
    "b64_png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 red pixel
    "caption": "🧪 Testing immediate Facebook posting from development app! #TestPost #DevMode",
    "time": "12:30",
    "publish_now": True  # KEY: Test immediate publishing
}

try:
    print("Testing immediate Facebook publishing...")
    response = requests.post(
        "http://localhost:8000/api/facebook/publish_binary",
        json=test_data,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Photo should be immediately published to Facebook!")
        print("Check your VoyeKat Facebook page to see the post.")
    else:
        print("❌ FAILED: Check the error above")
        
except Exception as e:
    print(f"❌ ERROR: {e}")