from backend.database.connection import engine
from backend.database.base import Base
# Import all models here so metadata is aware of them
from backend.models.user import User

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
