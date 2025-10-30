import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_voyekat_setup():
    """Test VoyeKat page setup"""
    
    page_id = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print("=== Testing VoyeKat Configuration ===")
    print(f"Page ID: {page_id}")
    print(f"Token: {token[:20] if token else 'None'}...")
    
    if page_id != "108496194378505":
        print("❌ Page ID not set to VoyeKat")
        return
        
    if token == "PLACEHOLDER_TOKEN_HERE":
        print("❌ Token still needs to be updated")
        print("   Please update FB_PAGE_ACCESS_TOKEN in .env with the actual VoyeKat token")
        return
    
    # Test page access
    try:
        url = f"https://graph.facebook.com/v24.0/{page_id}?access_token={token}"
        r = requests.get(url, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ SUCCESS: Connected to page '{data.get('name', 'Unknown')}'")
            print("🎉 Ready to test Facebook posting!")
        else:
            print(f"❌ Error: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_voyekat_setup()