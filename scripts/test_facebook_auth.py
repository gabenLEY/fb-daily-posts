"""
Test Facebook authentication endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_facebook_login_url():
    """Test Facebook login URL generation"""
    print("🧪 Testing Facebook Login URL")
    print("=" * 40)
    
    # First, we need to login to get a token
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    
    try:
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/user/login", json=login_data)
        login_result = login_response.json()
        
        if not login_result.get('success'):
            print(f"❌ Login failed: {login_result.get('error')}")
            return
        
        token = login_result.get('access_token')
        print(f"✅ Login successful, got token")
        
        # Now test Facebook login URL
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/facebook-auth/facebook/login-url", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"✅ Facebook login URL generated successfully!")
            print(f"🔗 URL: {data.get('login_url')}")
        else:
            print(f"❌ Failed to generate Facebook login URL: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_facebook_pages():
    """Test getting Facebook pages"""
    print("\n🧪 Testing Facebook Pages")
    print("=" * 40)
    
    # First, we need to login to get a token
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    
    try:
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/user/login", json=login_data)
        login_result = login_response.json()
        
        if not login_result.get('success'):
            print(f"❌ Login failed: {login_result.get('error')}")
            return
        
        token = login_result.get('access_token')
        
        # Now test Facebook pages
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/facebook-auth/pages", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run Facebook authentication tests"""
    print("🚀 Facebook Authentication Test Suite")
    print("=" * 50)
    
    test_facebook_login_url()
    test_facebook_pages()

if __name__ == "__main__":
    main()