from backend.config.settings import settings
from backend.models.user import User

def test_settings_loaded():
    assert settings.DATABASE_URL is not None
    assert "postgresql" in settings.DATABASE_URL

def test_user_model_has_table():
    assert User.__tablename__ == "users"
