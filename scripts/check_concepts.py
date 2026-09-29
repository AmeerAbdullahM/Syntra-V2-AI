import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.fusion import FusedConcept

def check():
    with SessionLocal() as db:
        concepts = db.query(FusedConcept).all()
        print(f"Total concepts: {len(concepts)}")
        for c in concepts:
            print(f"Concept: {c.title}, rock_id: {c.rock_id}")

if __name__ == "__main__":
    check()
