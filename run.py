"""
Main application entry point
"""
import os
import logging
from app import create_app

# Configure logging for debug information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

# Create the app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))  # Changed default port to match what we've been using
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'  # Enable debug by default
    
    print(f"🚀 Starting FB Daily Posts API on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Logging level: INFO")
    print(f"🌐 Access at: http://127.0.0.1:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)