from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    
    app.secret_key = os.environ.get("SECRET_KEY", "dev-key-fallback")

    #  CONFIGURACIÓN DE BASE DE DATOS
    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "postgresql+psycopg2://tu_usuario:tu_pass@localhost/tu_db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar DB y migraciones
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models
    
    # Registrar blueprints
    from .routes.panel import panel_bp
    from .routes.auth import auth_bp
    from .routes.calculadora import calculadora_bp
    from .routes.coach import coach_bp
    from app.routes.progreso import progreso_bp
    from app.routes.rutinas import rutinas_bp
    from app.routes.ejercicios import ejercicios_bp
    from app.routes.api import api_bp

    app.register_blueprint(panel_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calculadora_bp)
    app.register_blueprint(coach_bp) 
    app.register_blueprint(progreso_bp)
    app.register_blueprint(rutinas_bp)
    app.register_blueprint(ejercicios_bp)
    app.register_blueprint(api_bp)

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    return app
