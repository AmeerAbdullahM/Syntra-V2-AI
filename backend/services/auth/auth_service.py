from sqlalchemy.orm import Session
from backend.database.repositories.user_repo import UserRepository
from backend.schemas.auth import UserCreate, UserLogin, UserResponse
from backend.security.passwords import verify_password
import re

class AuthServiceError(Exception):
    pass

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> UserResponse:
        if self.repo.get_by_email(data.email):
            raise AuthServiceError("Email already registered.")
        
        # Basic validation
        if len(data.password) < 8:
            raise AuthServiceError("Password must be at least 8 characters long.")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data.email):
             raise AuthServiceError("Invalid email format.")

        user = self.repo.create(data)
        return UserResponse.model_validate(user)

    def login(self, data: UserLogin) -> UserResponse:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise AuthServiceError("Invalid email or password.")
        
        if not user.is_active:
            raise AuthServiceError("User account is disabled.")

        return UserResponse.model_validate(user)
