from flask import Blueprint, render_template, request, redirect, session
import bcrypt 

auth_bp = Blueprint("auth", __name__)

#HOME / LOGIN PAGE
@auth_bp.route("/", methods=["GET"])
def home():
    return render_template("public/index.html")

# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    password = request.form["password"]

    from app.db import get_conn 
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, contraseña, nombre, rol FROM usuarios WHERE correo = %s", (correo,))
        user = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not user:
        return "Usuario no encontrado"
    
    user_id, hashed_password, nombre, rol = user
    
    if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
        session["user_id"] = user_id
        session["rol"] = rol
        session["nombre"] = nombre
        return redirect("/panel")
    else:
        return "Contraseña incorrecta"

# LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
