import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.job import Job
from backend.models.material import Material

def check():
    with SessionLocal() as db:
        jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
        for j in jobs:
            print(f"Job {j.id} - Status: {j.status}")
            print(f"Error: {j.error_message}")
            
if __name__ == "__main__":
    check()
