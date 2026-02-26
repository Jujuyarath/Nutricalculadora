from flask import Blueprint, render_template, request, session, redirect

panel_bp = Blueprint("panel", __name__)

@panel_bp.route("/panel")
def panel():
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT nombre, rol FROM usuarios WHERE id = %s", (session["user_id"],))
        data = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not data:
        return "Usuario no encontrado"
    
    nombre, rol = data

    #MODO ADMIN: permite elegir panel
    modo = request.args.get("modo")

    if rol == "admin" and modo:
        if modo == "coach":
            return render_template("coach/panel_coach.html", nombre=nombre)
        if modo == "nutri":
            return render_template("nutri/panel_nutri.html", nombre=nombre)
        if modo == "cliente":
            return render_template("cliente/panel_cliente.html", nombre=nombre)
        if modo == "visualizacion":
            return render_template("cliente/panel_visualizacion.html", nombre=nombre)

    #PANEL ADMIN (MENU)
    if rol == "admin":
        return render_template("admin/panel_admin.html", nombre=nombre)
    
    #PANEL COACH
    elif rol == "coach":
        return render_template("coach/panel_coach.html", nombre=nombre)
    
    #PANEL NUTRIOLOGO
    elif rol == "nutri":
        return render_template("nutri/panel_nutri.html", nombre=nombre)
    
    #PANEL CLIENTE INDEPENDIENTE
    elif rol == "cliente_independiente":
        return render_template("cliente/panel_cliente.html", nombre=nombre)
    
    #PANEL CLIENTE ASIGNADO
    elif rol == "cliente_asignado":
        return render_template("cliente/panel_visualizacion.html", nombre=nombre)
    
    else:
        return "Rol no reconocido"
