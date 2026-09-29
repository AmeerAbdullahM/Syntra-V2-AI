import pytest
from backend.services.auth.auth_service import AuthService, AuthServiceError
from backend.schemas.auth import UserCreate, UserLogin
from backend.database.connection import SessionLocal
from backend.models.user import User

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_register_and_login(db_session):
    auth_service = AuthService(db_session)
    
    # Use unique email for test
    test_email = "test_auth@example.com"
    
    # Cleanup previous if exists
    existing = db_session.query(User).filter(User.email == test_email).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()
        
    # Register
    user_create = UserCreate(email=test_email, password="password123", display_name="Test User")
    user_res = auth_service.register(user_create)
    assert user_res.email == test_email
    
    # Login
    user_login = UserLogin(email=test_email, password="password123")
    login_res = auth_service.login(user_login)
    assert login_res.email == test_email
    
    # Login with wrong password
    with pytest.raises(AuthServiceError):
        auth_service.login(UserLogin(email=test_email, password="wrongpassword"))
