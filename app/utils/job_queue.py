"""
Job queue system for handling long-running tasks
"""
import uuid
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SimpleJobQueue:
    """Simple in-memory job queue for handling async tasks"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def create_job(self, job_type: str, data: Dict[str, Any]) -> str:
        """Create a new job and return job ID"""
        job_id = str(uuid.uuid4())
        
        with self.lock:
            self.jobs[job_id] = {
                'id': job_id,
                'type': job_type,
                'status': 'pending',
                'data': data,
                'result': None,
                'error': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        with self.lock:
            return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, status: str, result: Any = None, error: str = None):
        """Update job status and result"""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update({
                    'status': status,
                    'result': result,
                    'error': error,
                    'updated_at': datetime.utcnow()
                })
    
    def cleanup_old_jobs(self, max_age_hours: int = 1):
        """Remove jobs older than max_age_hours"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        with self.lock:
            expired_jobs = [
                job_id for job_id, job in self.jobs.items()
                if job['created_at'] < cutoff
            ]
            
            for job_id in expired_jobs:
                del self.jobs[job_id]

# Global job queue instance
job_queue = SimpleJobQueue()

def process_image_generation_job(job_id: str, prompt: str, size: str = '1024x1024'):
    """Process image generation in background thread"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🎨 Starting image generation job {job_id}")
        job_queue.update_job(job_id, 'processing')
        
        # Import here to avoid circular imports
        from app.providers.image_gen import generate_image
        
        # Generate the image
        result = generate_image(prompt, size=size, add_watermark=True)
        
        logger.info(f"✅ Image generation job {job_id} completed")
        job_queue.update_job(job_id, 'completed', result=result)
        
    except Exception as e:
        logger.error(f"❌ Image generation job {job_id} failed: {e}")
        job_queue.update_job(job_id, 'failed', error=str(e))

def start_image_generation_job(prompt: str, size: str = '1024x1024') -> str:
    """Start async image generation job"""
    job_id = job_queue.create_job('image_generation', {
        'prompt': prompt,
        'size': size
    })
    
    # Start background thread
    thread = threading.Thread(
        target=process_image_generation_job,
        args=(job_id, prompt, size)
    )
    thread.daemon = True
    thread.start()
    
    return job_id