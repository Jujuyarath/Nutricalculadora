import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import Flask, render_template, request, redirect, session
import math
import os
import threading
import bcrypt
import psycopg2

app = Flask(__name__)
app.secret_key = "1.3.6.4.2.3.45.2.34.523.5423.65_fsd.jyr.nsf.5425.dfg.43.df.sky.ky.gnf.543.dsfghsf."

conn = psycopg2.connect(
    host="dpg-d65t1c0gjchc73fh6i30-a.oregon-postgres.render.com",
    database="arathlabs_db",
    user="arathlabs_db_user",
    password="EVXGekJcJvVGGOnOUiGcOeTiBhUWEWKx"
)

#Esta funcion siguiente es para enviar correos

def enviar_correo(destinatario, asunto, contenido_html):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        sender={"email": "soporte@arathlabs.com", "name": "Arath Labs"},
        subject=asunto,
        html_content=contenido_html
    )

    try:
        api_instance.send_transac_email(email)
        return True
    except ApiException as e:
        print("Error al enviar correo:", e)
        return False
    
def calcular_medidas(sexo, peso, altura, cuello, abdomen=None, cintura=None, cadera=None):
    #1. calcular % de grasa con formula navy
    if sexo == "M":
        grasa = 495 / (1.0324 - 0.19077 * math.log10(abdomen - cuello) + 0.15456 * math.log10(altura)) - 450
    else:
        grasa = 495 / (1.29579 - 0.35004 * math.log10(cintura + cadera - cuello) + 0.22100 * math.log10(altura)) - 450

    #2. Masa grasa en kg 
    masa_grasa = peso * (grasa / 100)

    #3. Masa libre de grasa (FFM)
    ffm = peso - masa_grasa

    #4. Masa muscular (estimada)
    masa_muscular = ffm * 0.52

    #5. % muscular
    porcentaje_muscular = (masa_muscular / peso) * 100

    #6. IMC
    imc = peso / ((altura / 100) **2)

    #7. Relacion cintura-alura
    whtr = (cintura if sexo == "F" else abdomen) / altura

    #8. Regresar todo en un diccionario
    return {
        "grasa": round(grasa, 2),
        "masa_grasa": round(masa_grasa, 2),
        "ffm": round(ffm, 2),
        "masa_muscular": round(masa_muscular, 2),
        "porcentaje_muscular": round(porcentaje_muscular, 2),
        "imc": round(imc, 2),
        "whtr": round(whtr, 2)
    }

@app.route("/", methods=["GET", "POST"])
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

    return render_template("index.html", resultado=resultado, sexo=sexo)

import os 

@app.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    password = request.form["password"]

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

@app.route("/panel")
def panel():
    if "user_id" not in session:
        return redirect("/")
    
    cur = conn.cursor()
    cur.execute("SELECT rol FROM usuarios WHERE id = %s", (session["user_id"],))
    rol = cur.fetchone()[0]

    #MODO ADMIN: permite elegir panel
    modo = request.args.get("modo")

    if rol == "admin" and modo:
        if modo == "coach":
            return render_template("panel_coach.html", nombre=nombre)
        if modo == "nutri":
            return render_template("panel_nutri.html", nombre=nombre)
        if modo == "cliente":
            return render_template("panel_cliente.html", nombre=nombre)
        if modo == "visualizacion":
            return render_template("panel_visualizacion.html", nombre=nombre)

    #PANEL ADMIN (MENU)
    if rol == "admin":
        return render_template("panel_admin.html", nomre=nombre)
    
    #PANEL COACH
    elif rol == "coach":
        return render_template("panel_coach.html", nombre=nombre)
    
    #PANEL NUTRIOLOGO
    elif rol == "nutri":
        return render_template("panel_nutri.html", nombre=nombre)
    
    #PANEL CLIENTE INDEPENDIENTE
    elif rol == "cliente_independiente":
        return render_template("panel_cliente.html", nombre=nombre)
    
    #PANEL CLIENTE ASIGNADO
    elif rol == "cliente_asignado":
        return render_template("panel_visualizacion.html")
    
    else:
        return "Rol no reconocido"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/mis_clientes")
def mis_clientes():
    if "user_id" not in session:
        return redirect("/")
    
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

@app.route("/cliente/<int:cliente_id>")
def ver_cliente(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    cur = conn.cursor()

    # Verificar que el cliente pertenece al coach/nutri
    cur.execute("""
        SELECT 1 FROM asignaciones
        WHERE profesional_id = %s AND cliente_id = %s
    """, (session["user_id"], cliente_id))

    if cur.fetchone() is None:
        return "No tienes permiso para ver este cliente"
    
    # Obtener datos del cliente
    cur.execute("SELECT nombre FROM usuarios WHERE id = %s", (cliente_id,))
    nombre = cur.fetchone()[0]

    # Obtener historial
    cur.execute("""
        SELECT grasa, masa_muscular, imc, whtr, fecha
        FROM historial
        WHERE usuario_id = %s
        ORDER BY fecha DESC
    """, (cliente_id,))

    historial = cur.fetchall()

    return render_template("historial_cliente.html", nombre=nombre, historial=historial, cliente_id=cliente_id)

@app.route("/registrar/<int:cliente_id>", methods=["GET", "POST"])
def registrar(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    cur = conn.cursor()

    # Verificar que el cliente pertenece al coach/nutri
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

if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)