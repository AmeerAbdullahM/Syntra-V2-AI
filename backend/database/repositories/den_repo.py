from sqlalchemy.orm import Session
from backend.models.den import Den
from backend.schemas.den import DenCreate
from typing import List

class DenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, den_create: DenCreate) -> Den:
        db_den = Den(
            name=den_create.name,
            description=den_create.description,
            is_public="true" if den_create.is_public else "false",
            invite_code=den_create.invite_code,
            max_members=den_create.max_members
        )
        self.db.add(db_den)
        self.db.commit()
        self.db.refresh(db_den)
        return db_den

    def delete(self, den_id: str):
        den = self.get_by_id(den_id)
        if den:
            self.db.delete(den)
            self.db.commit()

    def get_by_id(self, den_id: str) -> Den | None:
        return self.db.query(Den).filter(Den.id == den_id).first()

    def list_all(self) -> List[Den]:
        return self.db.query(Den).all()
