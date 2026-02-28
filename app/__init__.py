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
    app.secret_key = "1.3.6.4.2.3.45.2.34.523.5423.65_fsd.jyr.nsf.5425.dfg.43.df.sky.ky.gnf.543.dsfghsf."

    #  CONFIGURACIÓN DE BASE DE DATOS
    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "postgresql+psycopg://tu_usuario:tu_pass@localhost/tu_db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar DB y migraciones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    from .routes.panel import panel_bp
    from .routes.auth import auth_bp
    from .routes.calculadora import calculadora_bp
    from .routes.coach import coach_bp

    app.register_blueprint(panel_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calculadora_bp)
    app.register_blueprint(coach_bp)  

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    return app
