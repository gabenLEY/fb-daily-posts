"""
Test script for user authentication endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_user_registration():
    """Test user registration"""
    print("🧪 Testing User Registration")
    print("=" * 40)
    
    # Test data
    user_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "password123",
        "connect_facebook": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/user/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            return data.get('access_token'), data.get('user')
        else:
            print(f"❌ Registration failed: {data.get('error')}")
            return None, None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None, None

def test_user_login():
    """Test user login"""
    print("\n🧪 Testing User Login")
    print("=" * 40)
    
    # Test data
    login_data = {
        "username": "testuser123",  # or use email: "test@example.com"
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/user/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            return data.get('access_token'), data.get('user')
        else:
            print(f"❌ Login failed: {data.get('error')}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_get_profile(token):
    """Test get user profile"""
    print("\n🧪 Testing Get Profile")
    print("=" * 40)
    
    if not token:
        print("❌ No token provided")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if not data.get('success'):
            print(f"❌ Get profile failed: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Get profile error: {e}")

def test_facebook_status(token):
    """Test Facebook connection status"""
    print("\n🧪 Testing Facebook Connection Status")
    print("=" * 40)
    
    if not token:
        print("❌ No token provided")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/user/facebook-connection-status", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if not data.get('success'):
            print(f"❌ Facebook status failed: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Facebook status error: {e}")

def main():
    """Run all tests"""
    print("🚀 User Authentication Test Suite")
    print("=" * 50)
    
    # Test registration
    token, user = test_user_registration()
    
    if not token:
        # If registration failed (user might already exist), try login
        token, user = test_user_login()
    
    if token:
        # Test profile retrieval
        test_get_profile(token)
        
        # Test Facebook status
        test_facebook_status(token)
        
        print(f"\n✅ Authentication tests completed successfully!")
        print(f"🔑 Access Token: {token[:50]}...")
        print(f"👤 User: {user.get('username')} ({user.get('email')})")
    else:
        print("\n❌ Authentication tests failed!")

if __name__ == "__main__":
    main()