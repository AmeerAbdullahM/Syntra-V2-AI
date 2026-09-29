import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.fusion import FusedConcept
from backend.models.rock import Rock

def backfill():
    with SessionLocal() as db:
        # Just grab the first rock for simplicity since they likely only have one main rock in this test
        rock = db.query(Rock).first()
        if rock:
            concepts = db.query(FusedConcept).filter(FusedConcept.rock_id == None).all()
            for c in concepts:
                c.rock_id = rock.id
            db.commit()
            print(f"Backfilled {len(concepts)} concepts to rock {rock.title}")

if __name__ == "__main__":
    backfill()
