import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.queue.interface import QueueInterface
from backend.models.job import Job, JobStatusEnum

class PostgresQueue(QueueInterface):
    def __init__(self, db: Session):
        self.db = db

    def enqueue(self, job_type: str, den_id: str, target_id: str, user_id: str, payload: Dict[str, Any]) -> str:
        job = Job(
            job_type=job_type,
            status=JobStatusEnum.PENDING.value,
            payload=json.dumps(payload),
            den_id=den_id,
            target_id=target_id,
            user_id=user_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job.id

    def dequeue(self, job_type: str) -> Optional[Dict[str, Any]]:
        # Use FOR UPDATE SKIP LOCKED to ensure workers don't grab the same job
        sql = text("""
            SELECT id, payload 
            FROM jobs 
            WHERE status = :status AND job_type = :job_type
            ORDER BY created_at ASC 
            FOR UPDATE SKIP LOCKED 
            LIMIT 1
        """)
        
        result = self.db.execute(sql, {"status": JobStatusEnum.PENDING.value, "job_type": job_type}).first()
        
        if result:
            job_id = result[0]
            payload_str = result[1]
            
            # Update status to processing
            update_sql = text("""
                UPDATE jobs 
                SET status = :new_status, started_at = :now
                WHERE id = :id
            """)
            self.db.execute(update_sql, {
                "new_status": JobStatusEnum.PROCESSING.value, 
                "now": datetime.now(timezone.utc),
                "id": job_id
            })
            self.db.commit()
            
            return {
                "job_id": job_id,
                "payload": json.loads(payload_str),
                "target_id": self.db.query(Job).filter(Job.id == job_id).first().target_id,
                "den_id": self.db.query(Job).filter(Job.id == job_id).first().den_id
            }
        
        return None

    def complete(self, job_id: str):
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatusEnum.COMPLETED.value
            job.completed_at = datetime.now(timezone.utc)
            self.db.commit()

    def fail(self, job_id: str, error_message: str):
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatusEnum.FAILED.value
            job.error_message = error_message
            self.db.commit()
