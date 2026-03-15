import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL no configurada")
        return

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    try:
        # Agregar columna descanso a la tabla ejercicios
        print("Agregando columna 'descanso' a la tabla 'ejercicios'...")
        cur.execute("ALTER TABLE ejercicios ADD COLUMN IF NOT EXISTS descanso INTEGER DEFAULT 60;")
        
        # Agregar columnas faltantes a historial si no existen
        print("Verificando columnas adicionales en 'historial'...")
        cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS cuello NUMERIC;")
        cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS abdomen NUMERIC;")
        cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS cintura NUMERIC;")
        cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS cadera NUMERIC;")
        cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS bíceps NUMERIC;")
        
        conn.commit()
        print("Migración completada exitosamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error durante la migración: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
