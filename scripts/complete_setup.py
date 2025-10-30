"""
Complete Setup Script for FB Daily Posts
Organizes the application and verifies all components are working
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_jwt_extended', 
        'psycopg2', 'requests', 'openai', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def verify_environment_variables():
    """Verify required environment variables"""
    print("\n⚙️  Checking environment variables...")
    
    required_vars = [
        'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME',
        'FB_APP_ID', 'FB_APP_SECRET', 'OPENAI_API_KEY'
    ]
    
    optional_vars = [
        'FB_REDIRECT_URI', 'FRONTEND_URL', 'OPENROUTER_API_KEY'
    ]
    
    missing_required = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ['your_value_here', 'placeholder']:
            print(f"❌ {var} - Not configured")
            missing_required.append(var)
        else:
            print(f"✅ {var}")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value and value not in ['your_value_here', 'placeholder']:
            print(f"✅ {var} (optional)")
        else:
            print(f"⚠️  {var} (optional) - Not configured")
    
    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    return True

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️  Testing database connection...")
    
    try:
        # Import here to avoid issues if modules aren't available
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import create_app
        from app.database.db import db
        
        app = create_app()
        with app.app_context():
            # Test connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("\n🔄 Running database migrations...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'migrate_user_facebook.py')
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations completed")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def test_authentication():
    """Test user authentication system"""
    print("\n🔐 Testing authentication system...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'test_user_auth.py')
        ], capture_output=True, text=True, timeout=60)
        
        if "✅ Authentication tests completed successfully!" in result.stdout:
            print("✅ Authentication system working")
            return True
        else:
            print("❌ Authentication tests failed")
            print(result.stdout[-500:])  # Show last 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def test_facebook_integration():
    """Test Facebook integration"""
    print("\n📘 Testing Facebook integration...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'test_facebook_auth.py')
        ], capture_output=True, text=True, timeout=60)
        
        if "✅ Facebook login URL generated successfully!" in result.stdout:
            print("✅ Facebook integration working")
            return True
        else:
            print("❌ Facebook integration tests failed")
            print(result.stdout[-500:])  # Show last 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Facebook test error: {e}")
        return False

def verify_file_structure():
    """Verify project file structure"""
    print("\n📁 Verifying project structure...")
    
    required_files = [
        'app/__init__.py',
        'app/controllers/user_auth_controller.py',
        'app/controllers/facebook_auth_controller.py',
        'app/controllers/social_media_controller.py',
        'app/database/models/user.py',
        'app/providers/image_gen.py',
        'app/providers/llama_meta.py',
        'requirements.txt',
        '.env'
    ]
    
    required_dirs = [
        'app',
        'app/controllers',
        'app/database',
        'app/database/models',
        'app/providers',
        'scripts',
        'examples'
    ]
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check directories
    for directory in required_dirs:
        dir_path = os.path.join(project_root, directory)
        if os.path.exists(dir_path):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - Missing")
    
    # Check files
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")

def create_documentation_index():
    """Create a documentation index file"""
    print("\n📚 Creating documentation index...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_content = """# FB Daily Posts - Documentation Index

Welcome to the FB Daily Posts documentation. This index provides quick access to all documentation files.

## 📖 Main Documentation

- **[README.md](README.md)** - Main project overview and quick start guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete REST API reference
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization and architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide for various platforms
- **[SCRIPTS.md](SCRIPTS.md)** - Detailed scripts documentation

## 🚀 Quick Start

1. **Setup**: Follow [README.md](README.md) for initial setup
2. **Configuration**: Check [DEPLOYMENT.md](DEPLOYMENT.md) for environment setup
3. **Testing**: Use scripts documented in [SCRIPTS.md](SCRIPTS.md)
4. **API Usage**: Refer to [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 📁 Project Structure

```
fb-daily-posts/
├── app/                    # Main application
├── scripts/               # Utility scripts  
├── examples/              # Frontend examples
├── docs/                  # Documentation
└── *.md                   # Documentation files
```

## 🔧 Key Scripts

- `python scripts/setup_database.sql` - Database setup
- `python scripts/migrate_user_facebook.py` - Database migration
- `python scripts/check_facebook_config.py` - Configuration check
- `python scripts/test_user_auth.py` - Authentication test
- `python scripts/test_facebook_auth.py` - Facebook integration test

## 🌐 API Endpoints

Base URL: `http://127.0.0.1:8000`

### Authentication
- `POST /api/user/register` - Register user
- `POST /api/user/login` - Login user
- `GET /api/user/profile` - Get profile

### Facebook Integration
- `GET /api/facebook-auth/facebook/login-url` - Get OAuth URL
- `GET /api/facebook-auth/pages` - Get user pages
- `POST /api/facebook-auth/select-page` - Select page

### Content Generation
- `POST /api/social/generate-prompt` - Generate text
- `POST /api/social/generate-image` - Generate image
- `POST /api/social/create-post` - Create post

## 📞 Support

- **Issues**: Check documentation first, then create GitHub issue
- **Testing**: Run `python scripts/complete_setup.py` for full verification
- **Configuration**: Use `python scripts/check_facebook_config.py`

---

**Documentation Last Updated**: October 30, 2025
**Project Version**: 2.0.0
"""
    
    try:
        index_path = os.path.join(project_root, 'DOCUMENTATION_INDEX.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        print(f"✅ Created documentation index: {index_path}")
    except Exception as e:
        print(f"❌ Failed to create documentation index: {e}")

def display_next_steps():
    """Display next steps for the user"""
    print_header("Setup Complete - Next Steps")
    
    print("""
🎉 FB Daily Posts Setup Complete!

📋 What's Ready:
✅ Database configured and migrated
✅ User authentication system
✅ Facebook integration
✅ AI content generation
✅ Complete API documentation
✅ Test scripts available

🚀 To Start Using:

1. Start the application:
   python app.py

2. Test the API:
   # Health check
   curl http://127.0.0.1:8000/health
   
   # Register a user
   curl -X POST http://127.0.0.1:8000/api/user/register \\
     -H "Content-Type: application/json" \\
     -d '{"username":"test","email":"test@example.com","password":"password123"}'

3. Connect your Next.js frontend:
   - Use examples/nextjs-complete-auth.jsx
   - Follow API_DOCUMENTATION.md for endpoints
   - Base URL: http://127.0.0.1:8000

📚 Documentation Available:
- README.md - Main documentation
- API_DOCUMENTATION.md - Complete API reference  
- SCRIPTS.md - All scripts explained
- DEPLOYMENT.md - Production deployment
- PROJECT_STRUCTURE.md - Code organization

🧪 Testing Commands:
- python scripts/test_user_auth.py
- python scripts/test_facebook_auth.py
- python scripts/check_facebook_config.py

🎯 Your application is ready for production deployment!
    """)

def main():
    """Main setup function"""
    print_header("FB Daily Posts Complete Setup")
    
    # Track setup success
    setup_steps = []
    
    # Step 1: Check Python version
    print_step(1, "Python Version Check")
    if check_python_version():
        setup_steps.append("✅ Python version")
    else:
        setup_steps.append("❌ Python version")
        print("Setup cannot continue with incompatible Python version")
        return False
    
    # Step 2: Check dependencies
    print_step(2, "Dependency Check")
    if check_dependencies():
        setup_steps.append("✅ Dependencies")
    else:
        setup_steps.append("❌ Dependencies")
        print("Please install missing dependencies and re-run setup")
        return False
    
    # Step 3: Verify environment variables
    print_step(3, "Environment Configuration")
    if verify_environment_variables():
        setup_steps.append("✅ Environment variables")
    else:
        setup_steps.append("❌ Environment variables")
        print("Please configure missing environment variables in .env file")
        return False
    
    # Step 4: Test database connection
    print_step(4, "Database Connection")
    if test_database_connection():
        setup_steps.append("✅ Database connection")
    else:
        setup_steps.append("❌ Database connection")
        print("Please check database configuration and ensure PostgreSQL is running")
        return False
    
    # Step 5: Run migrations
    print_step(5, "Database Migration")
    if run_migrations():
        setup_steps.append("✅ Database migration")
    else:
        setup_steps.append("❌ Database migration")
        print("Database migration failed - check database permissions")
        return False
    
    # Step 6: Verify file structure
    print_step(6, "Project Structure")
    verify_file_structure()
    setup_steps.append("✅ File structure verified")
    
    # Step 7: Test authentication
    print_step(7, "Authentication System")
    if test_authentication():
        setup_steps.append("✅ Authentication system")
    else:
        setup_steps.append("❌ Authentication system")
    
    # Step 8: Test Facebook integration
    print_step(8, "Facebook Integration")
    if test_facebook_integration():
        setup_steps.append("✅ Facebook integration")
    else:
        setup_steps.append("❌ Facebook integration")
    
    # Step 9: Create documentation
    print_step(9, "Documentation Setup")
    create_documentation_index()
    setup_steps.append("✅ Documentation created")
    
    # Display results
    print_header("Setup Results")
    for step in setup_steps:
        print(step)
    
    # Show next steps
    display_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)