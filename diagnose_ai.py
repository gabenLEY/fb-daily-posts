"""
Diagnostic script to check AI image generation setup
"""
import os
import sys

def check_environment():
    print("🔍 Checking AI Image Generation Setup\n")
    
    # Check OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OpenAI API Key: Configured (length: {len(openai_key)})")
    else:
        print("❌ OpenAI API Key: NOT CONFIGURED")
        print("   Add OPENAI_API_KEY to your .env file")
    
    # Check required packages
    required_packages = ['PIL', 'requests', 'uuid']
    
    print("\n📦 Checking Required Packages:")
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"✅ PIL (Pillow): {PIL.__version__}")
            elif package == 'requests':
                import requests
                print(f"✅ requests: {requests.__version__}")
            elif package == 'uuid':
                import uuid
                print(f"✅ uuid: Built-in module")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            if package == 'PIL':
                print("   Install with: pip install Pillow")
            elif package == 'requests':
                print("   Install with: pip install requests")
    
    # Check if image_gen can be imported
    print("\n🔧 Testing image_gen Import:")
    try:
        sys.path.append('app/providers')
        from image_gen import generate_image
        print("✅ image_gen imported successfully")
        
        # Test with a simple call
        print("\n🧪 Testing image generation (this may take time):")
        try:
            result = generate_image("test prompt", size="256x256")
            print(f"✅ Test generation successful: {result}")
        except Exception as e:
            print(f"❌ Test generation failed: {e}")
            
    except ImportError as e:
        print(f"❌ image_gen import failed: {e}")
    
    # Check watermark dependency
    print("\n🏷️  Checking Watermark Provider:")
    try:
        sys.path.append('app/providers')
        from watermark import apply_watermark
        print("✅ watermark provider imported successfully")
    except ImportError as e:
        print(f"❌ watermark import failed: {e}")
    
    # Check environment file
    print("\n📄 Checking Environment File:")
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("✅ OPENAI_API_KEY found in .env")
            else:
                print("❌ OPENAI_API_KEY not found in .env")
    else:
        print("❌ .env file not found")
        print("   Create .env file with OPENAI_API_KEY=your_key_here")
    
    print("\n" + "="*50)
    print("💡 SOLUTIONS:")
    if not openai_key:
        print("1. Add OpenAI API key to .env file:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
    
    print("2. Install missing packages:")
    print("   pip install Pillow requests")
    
    print("3. Get OpenAI API key from:")
    print("   https://platform.openai.com/api-keys")

if __name__ == "__main__":
    check_environment()