"""
Job model for storing async job data in database
"""
from app.database.db import db
from datetime import datetime
import json

class Job(db.Model):
    """Database model for async jobs"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, completed, failed
    data = db.Column(db.Text)  # JSON data for job parameters
    result = db.Column(db.Text)  # JSON result when completed
    error = db.Column(db.Text)  # Error message if failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'type': self.job_type,
            'status': self.status,
            'data': json.loads(self.data) if self.data else None,
            'result': json.loads(self.result) if self.result else None,
            'error': self.error,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def create_job(cls, job_id: str, job_type: str, data: dict):
        """Create a new job in database"""
        job = cls(
            id=job_id,
            job_type=job_type,
            status='pending',
            data=json.dumps(data) if data else None
        )
        db.session.add(job)
        db.session.commit()
        return job
    
    @classmethod
    def get_job(cls, job_id: str):
        """Get job by ID"""
        return cls.query.filter_by(id=job_id).first()
    
    def update_status(self, status: str, result=None, error=None):
        """Update job status and result"""
        self.status = status
        if result is not None:
            self.result = json.dumps(result)
        if error is not None:
            self.error = error
        self.updated_at = datetime.utcnow()
        db.session.commit()