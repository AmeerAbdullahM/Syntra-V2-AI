import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.connection import SessionLocal
from backend.services.auth.auth_service import AuthService
from backend.schemas.auth import UserCreate
from backend.config.settings import settings

def seed_superadmin():
    if not settings.SUPERADMIN_EMAIL or not settings.SUPERADMIN_PASSWORD:
        print("Superadmin credentials not found in settings.")
        return

    with SessionLocal() as db:
        auth_service = AuthService(db)
        from backend.database.repositories.user_repo import UserRepository
        user_repo = UserRepository(db)
        
        # Check if user exists
        existing_user = user_repo.get_by_email(settings.SUPERADMIN_EMAIL)
        if not existing_user:
            try:
                auth_service.register(UserCreate(
                    email=settings.SUPERADMIN_EMAIL,
                    display_name="Super Admin",
                    password=settings.SUPERADMIN_PASSWORD
                ))
                print(f"Superadmin {settings.SUPERADMIN_EMAIL} created successfully.")
            except Exception as e:
                print(f"Error creating superadmin: {e}")
        else:
            print("Superadmin already exists.")

if __name__ == "__main__":
    seed_superadmin()
