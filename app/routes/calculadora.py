from flask import Blueprint, render_template, request, redirect, session, current_app 
import threading
from app.utils.grasa import calcular_medidas 
from app.utils.correo import enviar_correo 

calculadora_bp = Blueprint("calculadora", __name__)

# RUTA PRINCIPAL (calculadora)
@calculadora_bp.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    sexo = None

    if request.method == "POST":
        enviar_entrenador = "enviar_entrenador" in request.form

        sexo = request.form["sexo"]
        peso = float(request.form["peso"])
        altura = float(request.form["altura"]) 
        cuello = float(request.form["cuello"])

        nombre = request.form["nombre"]
        correo_usuario = request.form["correo"]

        if sexo == "M":
            abdomen =float(request.form["abdomen"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, abdomen=abdomen)
        else:
            cintura = float(request.form["cintura"])
            cadera = float(request.form["cadera"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, cintura=cintura, cadera=cadera)
        
        #Aqui se crea el mensaje que se va a enviar 
        mensaje_html = f"""
        <h2>Hola {nombre}, aquí están tus resultados</h2>
        <p><strong>Grasa corporal:</strong> {resultado['grasa']}%</p>
        <p><strong>Masa grasa:</strong> {resultado['masa_grasa']} kg</p>
        <p><strong>Masa muscular:</strong> {resultado['masa_muscular']} kg</p>
        <p><strong>IMC:</strong> {resultado['imc']}</p>
        <p><strong>WHtR:</strong> {resultado['whtr']}</p>
        """
    
        #Enviar correo al usuario
        threading.Thread(target=enviar_correo, args=(correo_usuario, "Tus resultados por Arath Calderon", mensaje_html)).start()

        #Enviar copia al entrenador si marco la casilla
        if enviar_entrenador:
            threading.Thread(target=enviar_correo, args=("arath.cg73@gmail.com", "Resultados del cliente", mensaje_html)).start()

    return render_template("public/index.html", resultado=resultado, sexo=sexo)

# VER CLIENTE
@calculadora_bp.route("/cliente/<int:cliente_id>")
def ver_cliente(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    # ADMIN → acceso total
    if session.get("rol") != "admin":
        cur.execute("""
            SELECT 1 FROM asignaciones
            WHERE profesional_id = %s AND cliente_id = %s
        """, (session["user_id"], cliente_id))

        if cur.fetchone() is None:
            return "No tienes permiso para ver este cliente"

    # Obtener datos del cliente
    cur.execute("SELECT nombre FROM usuarios WHERE id = %s", (cliente_id,))
    row = cur.fetchone()

    if row is None:
        return "Cliente no encontrado"
    
    nombre = row[0]

    # Obtener historial
    cur.execute("""
        SELECT grasa, masa_muscular, imc, whtr, fecha
        FROM historial
        WHERE usuario_id = %s
        ORDER BY fecha DESC
    """, (cliente_id,))

    historial = cur.fetchall()

    return render_template("historial_cliente.html", nombre=nombre, historial=historial, cliente_id=cliente_id)

# REGISTRAR MEDIDAS
@calculadora_bp.route("/registrar/<int:cliente_id>", methods=["GET", "POST"])
def registrar(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    # ADMIN → acceso total
    if session.get("rol") != "admin":
        cur.execute("""
            SELECT 1 FROM asignaciones
            WHERE profesional_id = %s AND cliente_id = %s
        """, (session["user_id"], cliente_id))

        if cur.fetchone() is None:
            return "No tienes permiso para registrar medidas de este cliente"
    
    if request.method == "POST":
        grasa = request.form["grasa"]
        masa = request.form["masa"]
        imc = request.form["imc"]
        whtr = request.form["whtr"]

        cur.execute("""
            INSERT INTO historial (usuario_id, grasa, masa_muscular, imc, whtr)
            VALUES (%s, %s, %s, %s, %s)
        """, (cliente_id, grasa, masa, imc, whtr))

        conn.commit()

        return redirect(f"/cliente/{cliente_id}")
    
    return render_template("registrar.html", cliente_id=cliente_id)