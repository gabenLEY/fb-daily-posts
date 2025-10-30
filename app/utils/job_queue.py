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
                print(f"📝 Updating job {job_id} to status: {status}")
                job.update_status(status, result, error)
                print(f"✅ Job {job_id} updated successfully")
            else:
                print(f"❌ Job {job_id} not found in database for update")
        except Exception as e:
            print(f"⚠️ Database job update failed: {e}")
            import traceback
            print(f"⚠️ Traceback: {traceback.format_exc()}")
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
        logger.info(f"📦 Importing image_gen module for job {job_id}")
        from app.providers.image_gen import generate_image
        
        logger.info(f"🖼️ Calling generate_image for job {job_id} with prompt: {prompt[:50]}...")
        
        # Generate the image
        result = generate_image(prompt, size=size, add_watermark=True)
        
        logger.info(f"✅ Image generation job {job_id} completed with result keys: {list(result.keys()) if result else 'None'}")
        job_queue.update_job(job_id, 'completed', result=result)
        
    except ImportError as e:
        logger.error(f"❌ Import error in job {job_id}: {e}")
        job_queue.update_job(job_id, 'failed', error=f"Import error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Image generation job {job_id} failed: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        job_queue.update_job(job_id, 'failed', error=str(e))

def start_image_generation_job(prompt: str, size: str = '1024x1024') -> str:
    """Start async image generation job"""
    import logging
    logger = logging.getLogger(__name__)
    
    job_id = job_queue.create_job('image_generation', {
        'prompt': prompt,
        'size': size
    })
    
    logger.info(f"🚀 Created job {job_id}, starting background thread...")
    
    # Start background thread with better error handling
    def safe_process_job():
        try:
            logger.info(f"🧵 Background thread started for job {job_id}")
            
            # Get Flask app context for database operations
            from flask import current_app
            with current_app.app_context():
                process_image_generation_job(job_id, prompt, size)
        except Exception as e:
            logger.error(f"💥 Background thread crashed for job {job_id}: {e}")
            import traceback
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
            try:
                # Try to update job status even if main process failed
                from flask import current_app
                with current_app.app_context():
                    job_queue.update_job(job_id, 'failed', error=f"Thread error: {str(e)}")
            except Exception as update_error:
                logger.error(f"💥 Failed to update job status after thread crash: {update_error}")
    
    thread = threading.Thread(target=safe_process_job)
    thread.daemon = True
    thread.start()
    
    logger.info(f"✅ Background thread started for job {job_id}")
    
    return job_id