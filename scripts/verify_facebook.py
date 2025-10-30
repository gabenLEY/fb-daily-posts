import os, requests
from dotenv import load_dotenv

load_dotenv()

def verify_facebook_setup():
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    
    print("Verifying Facebook setup...")
    
    # Get information about the token
    print("\n1. Getting token info...")
    try:
        token_url = f"https://graph.facebook.com/v24.0/me?access_token={token}"
        r = requests.get(token_url, timeout=30)
        print(f"Token info status: {r.status_code}")
        print(f"Token info: {r.text}")
    except Exception as e:
        print(f"Token info error: {e}")
    
    # Get pages accessible by this token
    print("\n2. Getting accessible pages...")
    try:
        pages_url = f"https://graph.facebook.com/v24.0/me/accounts?access_token={token}"
        r = requests.get(pages_url, timeout=30)
        print(f"Pages status: {r.status_code}")
        print(f"Pages response: {r.text}")
        
        if r.status_code == 200:
            pages_data = r.json()
            if 'data' in pages_data and pages_data['data']:
                print("\nAvailable pages:")
                for page in pages_data['data']:
                    print(f"  - ID: {page.get('id', 'N/A')}")
                    print(f"    Name: {page.get('name', 'N/A')}")
                    print(f"    Access Token: {page.get('access_token', 'N/A')[:20]}...")
                    print()
            else:
                print("No pages found for this token")
    except Exception as e:
        print(f"Pages error: {e}")

if __name__ == "__main__":
    verify_facebook_setup()