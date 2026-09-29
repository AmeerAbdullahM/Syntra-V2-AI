from sqlalchemy.orm import Session
from backend.models.rock import Rock
from backend.schemas.rock import RockCreate
from typing import List

class RockRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RockCreate) -> Rock:
        rock = Rock(
            den_id=data.den_id,
            title=data.title,
            description=data.description,
            order_index=data.order_index
        )
        self.db.add(rock)
        self.db.commit()
        self.db.refresh(rock)
        return rock

    def get_by_id(self, rock_id: str) -> Rock | None:
        return self.db.query(Rock).filter(Rock.id == rock_id).first()

    def get_den_rocks(self, den_id: str) -> List[Rock]:
        return self.db.query(Rock).filter(Rock.den_id == den_id).order_by(Rock.order_index.asc()).all()

    def delete(self, rock_id: str):
        rock = self.get_by_id(rock_id)
        if rock:
            self.db.delete(rock)
            self.db.commit()
