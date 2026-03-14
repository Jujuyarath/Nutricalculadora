# app/db.py
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Fallback for local development if .env is not present
        database_url = "postgresql://tu_usuario:tu_pass@localhost/tu_db"
    
    # psycopg expects postgresql:// but some platforms like Heroku/Render provide postgres://
    # and SQLAlchemy sometimes uses postgresql+psycopg
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    if database_url.startswith("postgresql+psycopg://"):
        database_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    return psycopg.connect(database_url)