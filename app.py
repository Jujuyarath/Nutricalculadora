from flask import Flask, render_template, request
import math
import threading
import requests

app = Flask(__name__)

#Esta funcion siguiente es para enviar correos

def enviar_correo(destinatario, asunto, mensaje_html):
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "Arath Calderón", "email": "arath.cg73@gmail.com"},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "htmlContent": mensaje_html
    }

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

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

if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)