"""
Post model for managing social media posts
"""
from datetime import datetime
from app.database.db import db

class Post(db.Model):
    """Post model for social media content"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    caption = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    image_data = db.Column(db.Text)  # Base64 encoded image
    facebook_post_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    scheduled_time = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f'<Post {self.id}: {self.title or self.caption[:50]}>'
    
    def to_dict(self):
        """Convert post to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'caption': self.caption,
            'image_url': self.image_url,
            'facebook_post_id': self.facebook_post_id,
            'status': self.status,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'username': self.user.username if self.user else None
        }
    
    @classmethod
    def create_post(cls, user_id, caption, title=None, image_url=None, image_data=None,
                   scheduled_time=None, status='draft'):
        """Create a new post"""
        try:
            post = cls(
                user_id=user_id,
                title=title,
                caption=caption,
                image_url=image_url,
                image_data=image_data,
                status=status,
                scheduled_time=scheduled_time
            )
            
            db.session.add(post)
            db.session.commit()
            
            return post
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_by_id(cls, post_id):
        """Get post by ID"""
        return cls.query.filter_by(id=post_id).first()
    
    @classmethod
    def get_by_user(cls, user_id, limit=50, offset=0):
        """Get posts by user ID"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit)\
                       .offset(offset)\
                       .all()
    
    @classmethod
    def get_by_status(cls, status, limit=50, offset=0):
        """Get posts by status"""
        return cls.query.filter_by(status=status)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit)\
                       .offset(offset)\
                       .all()
    
    @classmethod
    def get_scheduled_posts(cls):
        """Get posts scheduled for publishing"""
        return cls.query.filter(cls.status == 'scheduled')\
                       .filter(cls.scheduled_time <= datetime.utcnow())\
                       .order_by(cls.scheduled_time.asc())\
                       .all()
    
    @classmethod
    def get_all_posts(cls, limit=50, offset=0):
        """Get all posts with user information"""
        return cls.query.join(cls.user)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit)\
                       .offset(offset)\
                       .all()
    
    def update_status(self, new_status):
        """Update post status"""
        try:
            self.status = new_status
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def mark_as_published(self, facebook_post_id=None):
        """Mark post as published"""
        try:
            self.status = 'published'
            self.published_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            if facebook_post_id:
                self.facebook_post_id = facebook_post_id
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def mark_as_failed(self):
        """Mark post as failed"""
        return self.update_status('failed')
    
    def delete(self):
        """Delete the post"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False