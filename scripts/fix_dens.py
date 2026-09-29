import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.models.den import Den

def fix_dens():
    with SessionLocal() as db:
        dens = db.query(Den).filter(Den.is_public == None).all()
        for den in dens:
            den.is_public = "true"
        db.commit()
        print(f"Fixed {len(dens)} dens.")

if __name__ == "__main__":
    fix_dens()
