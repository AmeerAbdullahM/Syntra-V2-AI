import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.job import Job

def check():
    with SessionLocal() as db:
        jobs = db.query(Job).filter(Job.job_type == "ROCK_FUSION").all()
        print(f"Total fusion jobs: {len(jobs)}")
        for j in jobs:
            print(f"Job: {j.id}, Status: {j.status}, Target: {j.target_id}, Error: {j.error_message}")

if __name__ == "__main__":
    check()
