# app/db.py
import psycopg
import os

def get_conn():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL no está configurada")
    
    # psycopg expects postgresql:// but some platforms like Heroku/Render provide postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return psycopg.connect(database_url)