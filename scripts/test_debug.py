import os
from dotenv import load_dotenv
from providers.llama_meta import refine_prompt_and_captions

load_dotenv()

# Test the function directly to see the error
try:
    print("Testing refine_prompt_and_captions function...")
    print(f"OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY')}")
    print(f"LLAMA_MODEL: {os.getenv('LLAMA_MODEL')}")
    
    result = refine_prompt_and_captions("test topic", "clean product shot")
    print("Success:", result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()