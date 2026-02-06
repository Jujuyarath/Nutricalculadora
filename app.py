from flask import Flask, render_template, request
import math

app = Flask(__name__)

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

    if request.method == "POST":
        sexo = request.form["sexo"]
        peso = float(request.form["peso"])
        altura = float(request.form["altura"]) 
        cuello = float(request.form["cuello"])

        if sexo == "M":
            abdomen =float(request.form["abdomen"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, abdomen=abdomen)
        else:
            cintura = float(request.form["cintura"])
            cadera = float(request.form["cadera"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, cintura=cintura, cadera=cadera)

    return render_template("index.html", resultado=resultado, sexo=sexo)

import os 

if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)