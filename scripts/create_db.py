import psycopg
from psycopg.errors import DuplicateDatabase
from backend.config.settings import settings

def create_database():
    # Convert postgresql+psycopg:// to postgresql://
    base_url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
    
    # We need to connect to the 'postgres' default database to create a new one
    # Replace the database name 'syntra_v2' with 'postgres' in the connection URL
    parts = base_url.rsplit('/', 1)
    if len(parts) == 2:
        conn_str = parts[0] + '/postgres'
    else:
        print("Invalid DATABASE_URL format")
        return
    
    try:
        with psycopg.connect(conn_str, autocommit=True) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("CREATE DATABASE syntra_v2")
                    print("Database 'syntra_v2' created successfully.")
                except DuplicateDatabase:
                    print("Database 'syntra_v2' already exists.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    create_database()
