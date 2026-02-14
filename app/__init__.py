from flask import Flask
import psycopg2

def create_app():
    app = Flask(__name__)
    app.secret_key = "1.3.6.4.2.3.45.2.34.523.5423.65_fsd.jyr.nsf.5425.dfg.43.df.sky.ky.gnf.543.dsfghsf."

    # Conexion a la base de datos
    app.conn = psycopg2.connect(
        host="dpg-d65t1c0gjchc73fh6i30-a.oregon-postgres.render.com",
        database="arathlabs_db",
        user="arathlabs_db_user",
        password="EVXGekJcJvVGGOnOUiGcOeTiBhUWEWKx",
        port="5432"
    )
    
    # Registrar blueprints
    from .routes.panel import panel_bp
    from .routes.auth import auth_bp
    from .routes.calculadora import calculadora_bp

    app.register_blueprint(panel_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calculadora_bp)
    
    return app