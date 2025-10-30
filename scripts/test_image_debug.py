import os
from dotenv import load_dotenv
from providers.image_gen import generate_image

load_dotenv()

# Test the generate_image function directly to see the error
try:
    print("Testing generate_image function...")
    print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")
    print(f"BASE_URL: {os.getenv('BASE_URL')}")
    print(f"BRAND_LOGO_PATH: {os.getenv('BRAND_LOGO_PATH')}")
    print(f"BRAND_LOGO_URL: {os.getenv('BRAND_LOGO_URL')}")
    
    result = generate_image("A modern smartphone on a clean white background", size="1024x1024", add_watermark=True)
    print("Success:", result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()