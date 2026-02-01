from flask import Flask, render_template, request
import math

app = Flask(__name__)

def calcular_grasa_navy(sexo, altura, cuello, abdomen=None, cintura=None, cadera=None):
    if sexo =="M":
        grasa = 86.010 *math.log10(abdomen - cuello) - 70.041 * math.log10(altura) + 36.76
    else:
        grasa = 163.205 * math.log10( cintura + cadera - cuello) - 97.684 * math.log10(altura) - 78.387
    return grasa

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":
        sexo = request.form["sexo"]
        altura = float(request.form["altura"]) 
        cuello = float(request.form["cuello"])

        if sexo == "M":
            abdomen =float(request.form["abdomen"])
            grasa = calcular_grasa_navy(sexo, altura, cuello, abdomen=abdomen)
        else:
            cintura = float(request.form["cintura"])
            cadera = float(request.form["cadera"])
            grasa = calcular_grasa_navy(sexo, altura, cuello, cintura=cintura, cadera=cadera)

        resultado = round(grasa, 2)

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)