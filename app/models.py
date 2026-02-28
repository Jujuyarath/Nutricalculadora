from . import db
from datetime import date

class Progreso(db.Model):
    __tablename__ = "progreso"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    rutina_id = db.Column(db.Integer, nullable=False)
    ejercicio_id = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, default=date.today)
    series_realizadas = db.Column(db.Integer)
    reps_realizadas = db.Column(db.Integer)
    peso_realizado = db.Column(db.Numeric)
    notas_cliente = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
