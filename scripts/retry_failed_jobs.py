import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.job import Job, JobStatusEnum
from backend.models.material import Material, MaterialStatusEnum

def retry_failed():
    with SessionLocal() as db:
        jobs = db.query(Job).filter(Job.status == JobStatusEnum.FAILED.value).all()
        for j in jobs:
            j.status = JobStatusEnum.PENDING.value
            j.error_message = None
            
            if j.job_type == "MATERIAL_PROCESS" and j.target_id:
                material = db.query(Material).filter(Material.id == j.target_id).first()
                if material:
                    material.processing_status = MaterialStatusEnum.QUEUED.value
                    
        db.commit()
        print(f"Re-queued {len(jobs)} failed jobs.")

if __name__ == "__main__":
    retry_failed()
