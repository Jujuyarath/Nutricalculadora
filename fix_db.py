from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate_db():
    with app.app_context():
        print("Iniciando migración desde el contexto de la aplicación...")
        
        try:
            # 1. Agregar columna descanso a ejercicios
            print("Verificando columna 'descanso' en 'ejercicios'...")
            db.session.execute(text("ALTER TABLE ejercicios ADD COLUMN IF NOT EXISTS descanso INTEGER DEFAULT 60;"))
            
            # 2. Agregar mediciones a historial si no existen
            print("Verificando columnas de mediciones en 'historial'...")
            columnas = [
                ("cuello", "NUMERIC"),
                ("abdomen", "NUMERIC"),
                ("cintura", "NUMERIC"),
                ("cadera", "NUMERIC"),
                ("brazo", "NUMERIC"),
                ("pierna", "NUMERIC"),
                ("peso", "NUMERIC"),
                ("altura", "NUMERIC")
            ]
            
            for col, tipo in columnas:
                db.session.execute(text(f"ALTER TABLE historial ADD COLUMN IF NOT EXISTS {col} {tipo};"))
                
            db.session.commit()
            print("Migración completada exitosamente.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate_db()
