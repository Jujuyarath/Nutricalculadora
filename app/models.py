from . import db
from datetime import date

class Rutina(db.Model):
    __tablename__ = "rutinas"

    id = db.Column(db.Integer, primary_key=True)
    profesional_id = db.Column(db.Integer)
    nombre = db.Column(db.String(100), nullable=False)
    objetivo = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

class RutinasAsignadas(db.Model):
    __tablename__ = "rutinas_asignadas"

    id = db.Column(db.Integer, primary_key=True)
    rutina_id = db.Column(db.Integer)
    cliente_id = db.Column(db.Integer)
    fecha_asignacio = db.Column(db.DateTime, server_default=db.func.now())

class Usuarios(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    correo = db.Column(db.Text, nullable=False)
    contraseña = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.now())
    rol = db.Column(db.Text, server_default='cliente_il')
    llave_acceso = db.Column(db.Text)

class Progreso(db.Model):
    __tablename__ = "progreso"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    rutina_id = db.Column(db.Integer, nullable=False)
    ejercicio_id = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date)
    series_realizada = db.Column(db.Integer)
    reps_realizadas = db.Column(db.Integer)
    peso_realizado = db.Column(db.Numeric)
    notas_cliente = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

class Historial(db.Model):
    __tablename__ = "historial"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer)
    grasa = db.Column(db.Numeric)
    masa_muscular = db.Column(db.Numeric)
    imc = db.Column(db.Numeric)
    whtr = db.Column(db.Numeric)
    fecha = db.Column(db.DateTime, server_default=db.func.now())

class EjerciciosBase(db.Model):
    __tablename__ = "ejercicios_base"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Ejercicios(db.Model):
    __tablename__ = "ejercicios"

    id = db.Column(db.Integer, primary_key=True)
    rutina_id = db.Column(db.Integer)
    nombre = db.Column(db.String(100), nullable=False)
    series = db.Column(db.Integer)
    repeticiones = db.Column(db.String(50))
    peso_sugerido = db.Column(db.String(50))
    notas = db.Column(db.Text)
    dia = db.Column(db.String(20))

class Asignaciones(db.Model):
    __tablename__ = "asignaciones"

    id = db.Column(db.Integer, primary_key=True)
    profesional_id = db.Column(db.Integer)
    cliente_id = db.Column(db.Integer)