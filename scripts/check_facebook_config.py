"""
Facebook Authentication Configuration Checker
Tests if the Facebook login implementation is properly configured
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_facebook_config():
    """Check Facebook authentication configuration"""
    
    print("🔍 Facebook Authentication Configuration Check")
    print("=" * 50)
    
    # Check environment variables
    fb_app_id = os.getenv('FB_APP_ID')
    fb_app_secret = os.getenv('FB_APP_SECRET')
    fb_redirect_uri = os.getenv('FB_REDIRECT_URI')
    frontend_url = os.getenv('FRONTEND_URL')
    
    # Legacy Facebook variables (for fallback)
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_page_token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    
    print("\n📋 Environment Variables:")
    print(f"  FB_APP_ID: {'✅ Set' if fb_app_id and fb_app_id != 'your_facebook_app_id_here' else '❌ Not configured'}")
    print(f"  FB_APP_SECRET: {'✅ Set' if fb_app_secret and fb_app_secret != 'your_facebook_app_secret_here' else '❌ Not configured'}")
    print(f"  FB_REDIRECT_URI: {'✅ Set' if fb_redirect_uri else '❌ Not set'} ({fb_redirect_uri})")
    print(f"  FRONTEND_URL: {'✅ Set' if frontend_url else '❌ Not set'} ({frontend_url})")
    print(f"  FB_PAGE_ID (fallback): {'✅ Set' if fb_page_id else '❌ Not set'}")
    print(f"  FB_PAGE_ACCESS_TOKEN (fallback): {'✅ Set' if fb_page_token else '❌ Not set'}")
    
    # Check if Facebook app is properly configured
    if fb_app_id and fb_app_id != 'your_facebook_app_id_here':
        print(f"\n📝 Facebook App ID: {fb_app_id}")
        
        # Generate example login URL
        redirect_uri = fb_redirect_uri or 'http://127.0.0.1:8000/api/facebook-auth/callback'
        scope = 'pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_metadata'
        example_state = '123'  # Example user ID
        
        login_url = (
            f"https://www.facebook.com/v19.0/dialog/oauth?"
            f"client_id={fb_app_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"state={example_state}"
        )
        
        print(f"\n🔗 Example Facebook Login URL:")
        print(f"  {login_url}")
    
    return {
        'app_id_configured': fb_app_id and fb_app_id != 'your_facebook_app_id_here',
        'app_secret_configured': fb_app_secret and fb_app_secret != 'your_facebook_app_secret_here',
        'redirect_uri_configured': bool(fb_redirect_uri),
        'frontend_url_configured': bool(frontend_url),
        'fallback_configured': bool(fb_page_id and fb_page_token)
    }

def test_facebook_endpoints():
    """Test Facebook authentication endpoints"""
    
    print("\n🧪 Testing Facebook Authentication Endpoints")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test endpoints that don't require authentication
    endpoints_to_test = [
        ("GET", "/api/facebook-auth/callback", "Should handle missing parameters"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        try:
            print(f"\n📡 Testing {method} {endpoint}")
            print(f"   {description}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=4)}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def check_database_migration():
    """Check if database has Facebook fields"""
    
    print("\n💾 Database Migration Check")
    print("=" * 50)
    
    try:
        import sys
        import os
        
        # Add the parent directory to Python path to import app
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import create_app
        from app.database.models.user import User
        from app.database.db import db
        
        app = create_app()
        with app.app_context():
            # Check if User model has Facebook fields
            user_table = User.__table__
            columns = [column.name for column in user_table.columns]
            
            facebook_fields = ['facebook_data', 'selected_page_id', 'selected_page_token']
            
            print("📊 User Model Columns:")
            for field in facebook_fields:
                status = "✅ Present" if field in columns else "❌ Missing"
                print(f"  {field}: {status}")
            
            if all(field in columns for field in facebook_fields):
                print("\n✅ Database migration appears complete!")
                return True
            else:
                print("\n❌ Database migration needed!")
                print("Run: python scripts/migrate_user_facebook.py")
                return False
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def main():
    """Main function to run all checks"""
    
    print("🚀 Facebook Authentication Implementation Check")
    print("=" * 70)
    
    # Check configuration
    config_status = check_facebook_config()
    
    # Check database migration
    db_status = check_database_migration()
    
    # Test endpoints
    test_facebook_endpoints()
    
    # Summary
    print("\n📋 Configuration Summary")
    print("=" * 50)
    
    if config_status['app_id_configured'] and config_status['app_secret_configured']:
        print("✅ Facebook App credentials configured")
    else:
        print("❌ Facebook App credentials missing")
        print("   → Update FB_APP_ID and FB_APP_SECRET in .env")
    
    if config_status['redirect_uri_configured']:
        print("✅ Redirect URI configured")
    else:
        print("❌ Redirect URI not configured")
        print("   → Set FB_REDIRECT_URI in .env")
    
    if db_status:
        print("✅ Database migration complete")
    else:
        print("❌ Database migration needed")
        print("   → Run: python scripts/migrate_user_facebook.py")
    
    if config_status['fallback_configured']:
        print("✅ Fallback credentials configured")
    else:
        print("⚠️  No fallback credentials (optional)")
    
    # Overall status
    all_configured = (
        config_status['app_id_configured'] and 
        config_status['app_secret_configured'] and 
        config_status['redirect_uri_configured'] and 
        db_status
    )
    
    print(f"\n🎯 Overall Status: {'✅ Ready for Facebook Login' if all_configured else '❌ Configuration Incomplete'}")
    
    if not all_configured:
        print("\n📝 Next Steps:")
        if not config_status['app_id_configured'] or not config_status['app_secret_configured']:
            print("  1. Create Facebook App at https://developers.facebook.com/")
            print("  2. Update FB_APP_ID and FB_APP_SECRET in .env")
        if not config_status['redirect_uri_configured']:
            print("  3. Set FB_REDIRECT_URI in .env")
        if not db_status:
            print("  4. Run database migration: python scripts/migrate_user_facebook.py")
        print("  5. Restart the Flask application")

if __name__ == "__main__":
    main()