import os, requests
from dotenv import load_dotenv

load_dotenv()

# Test the OpenAI API directly to see the exact error
try:
    print("Testing OpenAI API directly...")
    key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {"prompt": "A modern smartphone on a clean white background", "size": "1024x1024", "n": 1, "response_format": "b64_json"}
    
    print(f"API Key: {key[:20]}...")
    print(f"Request body: {body}")
    
    r = requests.post(url, headers=headers, json=body, timeout=120)
    
    print(f"Response status: {r.status_code}")
    print(f"Response headers: {dict(r.headers)}")
    print(f"Response text: {r.text}")
    
    if r.status_code == 200:
        print("Success!")
    else:
        print("Error occurred")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()