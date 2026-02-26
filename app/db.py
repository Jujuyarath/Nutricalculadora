# app/db.py
import psycopg

def get_conn():
    return psycopg.connect(
        host="dpg-d65t1c0gjchc73fh6i30-a.oregon-postgres.render.com",
        database="arathlabs_db",
        user="arathlabs_db_user",
        password="EVXGekJcJvVGGOnOUiGcOeTiBhUWEWKx",
        port="5432"
    )