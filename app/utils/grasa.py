import math

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