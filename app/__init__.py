"""
Flask Application Factory
Social Media Post Management System with JWT Authentication
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    # Configure Flask to use root-level static folder
    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(root_dir, 'static')
    
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Enable CORS
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Initialize database
    from app.database.db import init_database
    init_database(app)
    
    # Initialize JWT
    from app.database.auth import init_jwt
    init_jwt(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.post_routes import posts_bp
    from app.routes.social_routes import social_bp
    from app.controllers.facebook_auth_controller import facebook_auth_bp
    from app.controllers.user_auth_controller import user_auth_bp
    from app.controllers.simple_image_controller import simple_image_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_auth_bp, url_prefix='/api/user')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(facebook_auth_bp, url_prefix='/api/facebook-auth')
    app.register_blueprint(simple_image_bp, url_prefix='/api/image')
    
    # Create compatibility routes for old endpoints
    @app.route('/api/prompt', methods=['POST', 'OPTIONS'])
    def api_prompt_compat():
        """Compatibility route for /api/prompt -> /api/social/generate-prompt"""
        from flask import request, jsonify
        
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response
        
        # Forward to the actual endpoint
        from app.controllers.social_media_controller import generate_prompt
        return generate_prompt()
    
    @app.route('/api/generate-image', methods=['POST', 'OPTIONS'])
    def api_generate_image_compat():
        """Compatibility route for /api/generate-image -> /api/social/generate-image"""
        from flask import request, jsonify
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔄 Compatibility route called: {request.method} /api/generate-image")
        
        if request.method == 'OPTIONS':
            logger.info("✅ Handling OPTIONS request for CORS")
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response
        
        logger.info("🔄 Forwarding POST request to generate_image_endpoint")
        # Forward to the actual endpoint
        from app.controllers.social_media_controller import generate_image_endpoint
        return generate_image_endpoint()
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return {
            'status': 'healthy',
            'message': 'FB Daily Posts API is running',
            'version': '2.0.0',
            'architecture': 'MVC with Flask-SQLAlchemy and JWT'
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app