"""
Job queue system for handling long-running tasks
"""
import uuid
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class DatabaseJobQueue:
    """Database-backed job queue for handling async tasks across multiple processes"""
    
    def create_job(self, job_type: str, data: Dict[str, Any]) -> str:
        """Create a new job and return job ID"""
        job_id = str(uuid.uuid4())
        
        try:
            from app.database.models.job import Job
            Job.create_job(job_id, job_type, data)
            return job_id
        except Exception as e:
            # Fallback to in-memory if database fails
            print(f"⚠️ Database job creation failed, using in-memory: {e}")
            return self._create_memory_job(job_id, job_type, data)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        try:
            from app.database.models.job import Job
            job = Job.get_job(job_id)
            return job.to_dict() if job else None
        except Exception as e:
            print(f"⚠️ Database job lookup failed: {e}")
            return self._get_memory_job(job_id)
    
    def update_job(self, job_id: str, status: str, result: Any = None, error: str = None):
        """Update job status and result"""
        try:
            from app.database.models.job import Job
            job = Job.get_job(job_id)
            if job:
                job.update_status(status, result, error)
        except Exception as e:
            print(f"⚠️ Database job update failed: {e}")
            self._update_memory_job(job_id, status, result, error)
    
    # Fallback in-memory methods
    def __init__(self):
        self._memory_jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def _create_memory_job(self, job_id: str, job_type: str, data: Dict[str, Any]) -> str:
        with self._lock:
            self._memory_jobs[job_id] = {
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
    
    def _get_memory_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._memory_jobs.get(job_id)
    
    def _update_memory_job(self, job_id: str, status: str, result: Any = None, error: str = None):
        with self._lock:
            if job_id in self._memory_jobs:
                self._memory_jobs[job_id].update({
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
job_queue = DatabaseJobQueue()

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