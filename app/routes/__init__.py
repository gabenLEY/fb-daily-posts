"""
Routes package initialization
"""
from .auth_routes import auth_bp
from .post_routes import posts_bp
from .social_routes import social_bp

def register_routes(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(social_bp)

__all__ = ['auth_bp', 'posts_bp', 'social_bp', 'register_routes']