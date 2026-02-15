from flask import Blueprint, render_template, session, redirect, current_app

coach_bp = Blueprint("coach", __name__)

@coach_bp.route("/mis_clientes")
def mis_clientes():
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    # Obtener clientes asignados al coach
    if session.get("rol") == "admin":
        cur.execute("""
            SELECT u.id, u.nombre,
                    COALESCE(h.grasa, '—') AS grasa,
                    COALESCE(h.fecha, '—') AS fecha
            FROM usuarios u
            LEFT JOIN (
                SELECT usuario_id, grasa, fecha
                FROM historial
                ORDER BY fecha DESC
            ) h ON h.usuario_id = u.id
            WHERE u.rol = 'cliente'
            GROUP BY u.id, u.nombre, h.grasa, h.fecha
            ORDER BY u.nombre ASC 
        """) 
    
    else:
        # Si es COACH → ver solo sus clientes asignados
        cur.execute("""
            SELECT u.id, u.nombre,
                    COALESCE(h.grasa, '—') AS grasa,
                    COALESCE(h.fecha, '—') AS fecha
            FROM asignaciones a
            JOIN usuarios u ON u.id = a.cliente_id
            LEFT JOIN (
                SELECT usuario_id, grasa, fecha
                FROM historial
                ORDER BY fecha DESC
            ) h ON h.usuario_id = u.id
            WHERE a.profesional_id = %s
            GROUP BY u.id, u.nombre, h.grasa, h.fecha
            ORDER BY u.nombre ASC
        """, (session["user_id"],))

    clientes = cur.fetchall()

    return render_template("coach/mis_clientes.html", clientes=clientes)

# CREAR RUTINA
@coach_bp.route("/crear_rutina", methods=["GET", "POST"])
def crear_rutina():
    if "user_id" not in session:
        return redirect("/")
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        objetivo = request.form["objetivo"]

        conn = current_app.conn
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO rutinas (profesional_id, nombre, objetivo)
            VALUES (%s, %s, %s) RETURNING id
        """, (session["user_id"], nombre, objetivo))

        rutina_id = cur.fetchone()[0]
        conn.commit()

        return redirect(f"/editar_rutina/{rutina_id}")
    
    return render_template("coach/crear_rutina.html")

# EDITAR RUTINA
@coach_bp.route("/editar_rutina/<int:rutina_id>", methods=["GET", "POST"])
def editar_rutina(rutina_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        series = request.form["series"]
        repeticiones = request.form["repeticiones"]
        peso = request.form["peso"]
        notas = request.form["notas"]

        cur.execute("""
            INSERT INTO ejercicios (rutina_id, nombre, series, repeticiones, peso_sugerido, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rutina_id, nombre, series, repeticiones, peso, notas))

        conn.commit()

    # OBTENER EJERCICIOS EXISTENTES
    cur.execute("SELECT * FROM ejercicios WHERE rutina_id = %s", (rutina_id,))
    ejercicios = cur.fetchall()

    return render_template("coach/editar_rutina.html", ejercicios=ejercicios, rutina_id=rutina_id)

# ASIGNAR RUTINA A UN CLIENTE
@coach_bp.route("/asignar_rutina/<int:cliente_id>", methods=["GET", "POST"])
def asignar_rutina(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    if session.get("rol") != "admin":
        cur.execute("""
            SELECT 1 FROM asignaciones
            WHERE profesional_id = %s AND cliente_id = %s
        """, (session["user_id"], cliente_id))

        if cur.fetchone() is None:
            return "No tienes permiso para ver este cliente"
  
    if request.method == "POST":
        rutina_id = request.form["rutina_id"]

        cur.execute("""
            INSERT INTO rutinas_asignadas (rutina_id, cliente_id)
            VALUES (%s, %s)
        """, (rutina_id, cliente_id))

        conn.commit()
        return redirect(f"/cliente/{cliente_id}")
    
    # OBTENER RUTINAS DEL COACH
    cur.execute("""
        SELECT id, nombre FROM rutinas
        WHERE profesional_id = %s
    """, (session["user_id"],))

    rutinas = cur.fetchall()

    return render_template("coach/asignar_rutina.html", rutinas=rutinas, cliente_id=cliente_id)

@coach_bp.route("/progreso/<int:cliente_id>")
def progreso(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = current_app.conn
    cur = conn.cursor()

    if session.get("rol") != "admin":
        cur.execute("""
            SELECT 1 FROM asignaciones
            WHERE profesional_id = %s AND cliente_id = %s
        """, (session["user_id"], cliente_id))

        if cur.fetchone() is None:
            return "No tienes permiso para ver este progreso"
    
    # Obtener nombre del cliente
    cur.execute("SELECT nombre FROM usuarios WHERE id = %s", (cliente_id,))
    nombre = cur.fetchone()[0]

    # Obtener historial
    cur.execute("""
        SELECT grasa, masa_muscular, imc, whtr, fecha
        FROM historial
        WHERE usuario_id = %s
        ORDER BY fecha ASC
    """, (cliente_id,))

    datos = cur.fetchall()

    # Preparar datos para Chart.js
    fechas = [str(d[4]) for d in datos]
    grasa = [float(d[0]) for d in datos]
    masa = [float(d[1]) for d in datos]
    imc = [float(d[2]) for d in datos]
    whtr = [float(d[3]) for d in datos]

    return render_template(
        "coach/progreso.html",
        nombre=nombre,
        fechas=fechas,
        grasa=grasa,
        masa=masa,
        imc=imc,
        whtr=whtr
    )