from flask import Blueprint, request, jsonify
from app.database.auth import auth_required
from app.database.models.post import Post
from app.database.models.user import User
from app.database.db import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

post_bp = Blueprint('posts', __name__)

@post_bp.route('/', methods=['GET'])
@auth_required
def get_user_posts():
    """Get all posts for the authenticated user"""
    try:
        current_user_id = request.user_id
        posts = Post.get_by_user(current_user_id)
        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'count': len(posts)
        }), 200
    except Exception as e:
        logger.error(f"Error getting user posts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve posts'}), 500

@post_bp.route('/', methods=['POST'])
@auth_required
def create_post():
    """Create a new post for the authenticated user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_user_id = request.user_id
        
        # Validate required fields
        required_fields = ['content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: content'}), 400
        
        # Create the post
        post = Post.create_post(
            user_id=current_user_id,
            content=data['content'],
            platform=data.get('platform', 'facebook'),
            scheduled_time=data.get('scheduled_time'),
            media_urls=data.get('media_urls', [])
        )
        
        if post:
            return jsonify({
                'message': 'Post created successfully',
                'post': post.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Failed to create post'}), 500
            
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return jsonify({'error': 'Failed to create post'}), 500

@post_bp.route('/<int:post_id>', methods=['GET'])
@auth_required
def get_post(post_id):
    """Get a specific post by ID"""
    try:
        current_user_id = request.user_id
        post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error getting post {post_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve post'}), 500

@post_bp.route('/<int:post_id>', methods=['PUT'])
@auth_required
def update_post(post_id):
    """Update a specific post"""
    try:
        current_user_id = request.user_id
        post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'content' in data:
            post.content = data['content']
        if 'platform' in data:
            post.platform = data['platform']
        if 'scheduled_time' in data:
            post.scheduled_time = data['scheduled_time']
        if 'media_urls' in data:
            post.media_urls = data['media_urls']
        if 'status' in data:
            post.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update post'}), 500

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@auth_required
def delete_post(post_id):
    """Delete a specific post"""
    try:
        current_user_id = request.user_id
        post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete post'}), 500

@post_bp.route('/scheduled', methods=['GET'])
@auth_required
def get_scheduled_posts():
    """Get all scheduled posts for the authenticated user"""
    try:
        current_user_id = request.user_id
        posts = Post.query.filter_by(
            user_id=current_user_id, 
            status='scheduled'
        ).order_by(Post.scheduled_time).all()
        
        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'count': len(posts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scheduled posts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve scheduled posts'}), 500

@post_bp.route('/published', methods=['GET'])
@auth_required
def get_published_posts():
    """Get all published posts for the authenticated user"""
    try:
        current_user_id = request.user_id
        posts = Post.query.filter_by(
            user_id=current_user_id, 
            status='published'
        ).order_by(Post.created_at.desc()).all()
        
        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'count': len(posts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting published posts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve published posts'}), 500

@post_bp.route('/<int:post_id>/publish', methods=['POST'])
@auth_required
def publish_post(post_id):
    """Publish a specific post immediately"""
    try:
        current_user_id = request.user_id
        post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if post.status == 'published':
            return jsonify({'error': 'Post is already published'}), 400
        
        # Update post status to published
        post.status = 'published'
        post.published_at = db.func.now()
        db.session.commit()
        
        # Here you would integrate with actual social media APIs
        # For now, we'll just mark it as published
        
        return jsonify({
            'message': 'Post published successfully',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to publish post'}), 500