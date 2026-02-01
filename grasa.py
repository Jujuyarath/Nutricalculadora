import math
print("\n==========================================") 
print(" CÁLCULO DE GRASA CORPORAL (NAVY)")
print("==========================================\n")

def pedir_float(mensaje):
    while True:
        try:
            valor = float(input(mensaje))
            return valor
        except ValueError:
            print("Error: escribe un numero valido.")

# Declaramos variables
sexo = input("Sexo (M/F): ").upper()
if sexo not in ["M", "F"]:
    print("Error: escribe M para hombre o F para mujer")
    exit()

altura = pedir_float("Altura en cm: ")
cuello = pedir_float("Circunferencia de cuello en cm: ")
print("--------------------------------------------")

# Empezamos el codigo
if sexo == "M":
    abdomen = pedir_float("Circunferencia de abdomen: ")
    grasa = 86.010 * math.log10(abdomen - cuello) - 70.041 * math.log10(altura) + 36.76
elif sexo == "F":
    cintura = pedir_float("Circunferencia de cintura: ")
    cadera = pedir_float("Circunferencia de cadera: ")
    grasa = 163.205 * math.log10(cintura + cadera - cuello) - 97.684 * math.log10(altura) - 78.387
else:
    print ("sexo no valido.")
    exit()
print("\n------------------------------------------")
print(f"\nPorcentaje de grasa corporal: {grasa:.2f}%")

#Codigo del porcentaje de grasa
peso = pedir_float("Peso en kg: ")
masa_grasa = peso * (grasa / 100)
masa_magra = peso - masa_grasa
print("-------------------------------------------")
print (f"Masa grasa: {masa_grasa:.2f} kg")
print(f"Masa magra: {masa_magra:.2f} kg")

#Clasificacion
if sexo == "M":
    if grasa < 6:
        categoria = "Esencial"
    elif grasa < 14:
        categoria = "Atleta"
    elif grasa < 18:
        categoria = "Fitness"
    elif grasa < 25:
        categoria = "Aceptable"
    else:
        categoria = "Obesidad"
    
elif sexo == "F":
    if grasa < 14:
        categoria = "Esencial"
    elif grasa < 21:
        categoria = "Atleta"
    elif grasa < 25:
        categoria = "Fitness"
    elif grasa < 32:
        categoria = "Aceptable"
    else:
        categoria = "Obesidad"
print("-------------------------------------------")
print (f"Clasicicacion: {categoria}")
print("--------------------------------------------")