from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.auth import UserCreate
from backend.security.passwords import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_create: UserCreate) -> User:
        db_user = User(
            email=user_create.email,
            password_hash=get_password_hash(user_create.password),
            display_name=user_create.display_name
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_all(self):
        return self.db.query(User).all()
        
    def delete_user(self, user_id: str):
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
