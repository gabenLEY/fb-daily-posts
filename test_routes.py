"""
Route testing script to verify all API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_routes():
    print("🧪 Testing FB Daily Posts API Routes\n")
    
    # Test health endpoints
    print("1. Health Check Endpoints:")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   GET / -> {response.status_code} - {response.json()}")
        
        response = requests.get(f"{BASE_URL}/health")
        print(f"   GET /health -> {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    print("\n2. Authentication Endpoints:")
    # Test auth endpoints (these should return 400 for missing data, not 404)
    auth_endpoints = [
        ("POST", "/api/auth/register"),
        ("POST", "/api/auth/login"),
    ]
    
    for method, endpoint in auth_endpoints:
        try:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {method} {endpoint} -> {response.status_code}")
        except Exception as e:
            print(f"   ❌ {method} {endpoint} failed: {e}")
    
    print("\n3. Social Media / AI Endpoints:")
    # Test the prompt endpoints
    social_endpoints = [
        ("OPTIONS", "/api/prompt"),
        ("POST", "/api/prompt"),
        ("POST", "/api/social/generate-prompt"),
        ("POST", "/api/social/generate-image"),
        ("GET", "/api/social/facebook-config"),
    ]
    
    for method, endpoint in social_endpoints:
        try:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            elif method == "OPTIONS":
                response = requests.options(f"{BASE_URL}{endpoint}")
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {method} {endpoint} -> {response.status_code}")
        except Exception as e:
            print(f"   ❌ {method} {endpoint} failed: {e}")
    
    print("\n4. Post Management Endpoints:")
    # Test post endpoints (these need auth, so should return 401 or similar)
    post_endpoints = [
        ("GET", "/api/posts/"),
        ("POST", "/api/posts/"),
        ("GET", "/api/posts/scheduled"),
        ("GET", "/api/posts/published"),
    ]
    
    for method, endpoint in post_endpoints:
        try:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {method} {endpoint} -> {response.status_code}")
        except Exception as e:
            print(f"   ❌ {method} {endpoint} failed: {e}")
    
    print("\n✅ Route testing completed!")
    print("\nExpected status codes:")
    print("- 200: Success")
    print("- 400: Bad Request (missing data)")
    print("- 401: Unauthorized (missing JWT token)")
    print("- 404: Not Found (route doesn't exist)")

if __name__ == "__main__":
    test_routes()