# app/db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Fallback for local development if .env is not present
        database_url = "postgresql://tu_usuario:tu_pass@localhost/tu_db"
    
    # psycopg2 expects postgresql:// but some platforms like Heroku/Render provide postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    if "postgresql+psycopg" in database_url:
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://", 1)
        database_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    return psycopg2.connect(database_url)