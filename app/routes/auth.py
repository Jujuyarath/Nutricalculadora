from flask import Blueprint, render_template, request, redirect, session, current_app
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

    conn = current_app.conn
    cur = conn.cursor()
    cur.execute("SELECT id, contraseña FROM usuarios WHERE correo = %s", (correo,))
    user = cur.fetchone()

    if not user:
        return "Usuario no encontrado"
    
    user_id, hashed_password = user
    
    if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
        session["user_id"] = user_id
        return redirect("/panel")
    else:
        return "Contraseña incorrecta"

# LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@auth_bp.route("/mis_clientes")
def mis_clientes():
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    # Verificar rol
    cur.execute("SELECT rol FROM usuarios WHERE id = %s", (session["user_id"],))
    rol = cur.fetchone()[0]

    if rol not in ("coach", "nutri"):
        return "No tienes permiso para ver esta página"
    
    # Obtener clientes asignados
    cur.execute("""
        SELECT u.id, u.nombre, u.correo
        FROM asignaciones a
        JOIN usuarios u ON a.cliente_id = u.id
        WHERE a.profesional_id = %s
    """, (session["user_id"],))

    clientes = cur.fetchall()

    return render_template("mis_clientes.html", clientes=clientes)
