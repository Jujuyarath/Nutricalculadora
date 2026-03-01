from flask import Blueprint, render_template, request, redirect, session, jsonify
import bcrypt 
from app.utils.auth import generar_token, token_required
from app.utils.models import Usuarios

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

# LOGIN API (APP MÓVIL)
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    correo = data.get("correo")
    password = data.get("password")

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
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    user_id, hashed_password, nombre, rol = user

    if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):

        from app.utils.auth import generar_token
        token = generar_token(user_id)

        return jsonify({
            "mensaje": "Login exitoso",
            "token": token,
            "usuario_id": user_id,
            "nombre": nombre,
            "rol": rol
        }), 200
    
    else:
        return jsonify({"error": "Contraseña incorrecta"}), 401
    
@auth_bp.route('/api/perfil', methods=['GET'])
@token_required
def api_perfil(usuario_actual):
    usuario = Usuarios.query.get(usuario_actual)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    }), 200