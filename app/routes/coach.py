from flask import Blueprint, render_template, session, redirect, request, jsonify
import bcrypt

coach_bp = Blueprint("coach", __name__)

@coach_bp.route("/mis_clientes")
def mis_clientes():
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    # Obtener clientes asignados al coach
    try:
        if session.get("rol") == "admin":
            cur.execute("""
                SELECT 
                    u.id, 
                    u.nombre,
                    (
                        SELECT grasa
                        FROM historial 
                        WHERE usuario_id = u.id 
                        ORDER BY fecha DESC 
                        LIMIT 1
                    ) AS grasa,
                    (
                        SELECT fecha 
                        FROM historial 
                        WHERE usuario_id = u.id 
                        ORDER BY fecha DESC
                        LIMIT 1
                    ) AS fecha
                FROM usuarios u
                WHERE u.rol = 'cliente'
                ORDER BY u.nombre ASC;
            """)
    
        else:
        # Si es COACH → ver solo sus clientes asignados
            cur.execute("""
                SELECT 
                    u.id, 
                    u.nombre,
                    (
                        SELECT grasa 
                        FROM historial
                        WHERE usuario_id = u.id 
                        ORDER BY fecha DESC 
                        LIMIT 1
                    ) AS grasa,
                    (
                        SELECT fecha 
                        FROM historial 
                        WHERE usuario_id = u.id 
                        ORDER BY fecha DESC 
                        LIMIT 1
                    ) AS fecha
                FROM asignaciones a
                JOIN usuarios u ON u.id = a.cliente_id
                WHERE a.profesional_id = %s
                ORDER BY u.nombre ASC;
            """, (session["user_id"],))

        clientes = cur.fetchall()
        return render_template("coach/mis_clientes.html", clientes=clientes)

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# CREAR RUTINA
@coach_bp.route("/crear_rutina", methods=["GET", "POST"])
def crear_rutina():
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":
        try:
            nombre = request.form["nombre"]
            objetivo = request.form["objetivo"]

        

            cur.execute("""
                INSERT INTO rutinas (profesional_id, nombre, objetivo)
                VALUES (%s, %s, %s) RETURNING id
            """, (session["user_id"], nombre, objetivo))

            rutina_id = cur.fetchone()[0]
            conn.commit()

            return redirect(f"/editar_rutina/{rutina_id}")
    
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    cur.close()
    conn.close()
    return render_template("coach/crear_rutina.html")

# EDITAR RUTINA
@coach_bp.route("/editar_rutina/<int:rutina_id>", methods=["GET", "POST"])
def editar_rutina(rutina_id):
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":
        try:
            dia = request.form["dia"]
            nombre = request.form["nombre"]
            series = request.form["series"]
            repeticiones = request.form["repeticiones"]
            peso = request.form["peso"]
            notas = request.form["notas"]

            cur.execute("""
                INSERT INTO ejercicios (rutina_id, nombre, series, repeticiones, peso_sugerido, notas, dia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (rutina_id, nombre, series, repeticiones, peso, notas, dia))

            conn.commit()

        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            raise e

    # OBTENER EJERCICIOS EXISTENTES
    try:
        cur.execute("""
            SELECT id, dia, nombre, series, repeticiones, peso_sugerido, notas
            FROM ejercicios
            WHERE rutina_id = %s
            ORDER BY 
                CASE dia
                    WHEN 'Lunes' THEN 1
                    WHEN 'Martes' THEN 2
                    WHEN 'Miércoles' THEN 3
                    WHEN 'Jueves' THEN 4
                    WHEN 'Viernes' THEN 5
                    WHEN 'Sábado' THEN 6
                    WHEN 'Domingo' THEN 7
                END,
                id ASC
        """, (rutina_id,))

        ejercicios = cur.fetchall()

        # Agrupar ejercicios por día
        dias_dict = {}
        for e in ejercicios:
            dia = e[1]
            if dia not in dias_dict:
                dias_dict[dia] = []
            dias_dict[dia].append(e)
            
        return render_template("coach/editar_rutina.html", dias_dict=dias_dict, rutina_id=rutina_id)
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# ASIGNAR RUTINA A UN CLIENTE
@coach_bp.route("/asignar_rutina/<int:cliente_id>", methods=["GET", "POST"])
def asignar_rutina(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        if session.get("rol") != "admin":
            cur.execute("""
                SELECT 1 FROM asignaciones
                WHERE profesional_id = %s AND cliente_id = %s
            """, (session["user_id"], cliente_id))

            if cur.fetchone() is None:
                cur.close()
                conn.close()
                return "No tienes permiso para ver este cliente"
  
        if request.method == "POST":
            rutina_id = request.form["rutina_id"]

            cur.execute("""
                INSERT INTO rutinas_asignadas (rutina_id, cliente_id)
                VALUES (%s, %s)
            """, (rutina_id, cliente_id))

            conn.commit()
            cur.close()
            conn.close()
            return redirect(f"/cliente/{cliente_id}")

        cur.execute("""
            SELECT id, nombre FROM rutinas
            WHERE profesional_id = %s
        """, (session["user_id"],))

        rutinas = cur.fetchall()
        return render_template("coach/asignar_rutina.html", rutinas=rutinas, cliente_id=cliente_id)

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if not cur.closed:
            cur.close()
        if not conn.closed:
            conn.close()
    
@coach_bp.route("/progreso/<int:cliente_id>")
def progreso(cliente_id):
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        if session.get("rol") != "admin":
            cur.execute("""
                SELECT 1 FROM asignaciones
                WHERE profesional_id = %s AND cliente_id = %s
            """, (session["user_id"], cliente_id))

            if cur.fetchone() is None:
                cur.close()
                conn.close()
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
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if not cur.closed:
            cur.close()
        if not conn.closed:
            conn.close()

# Autocompletar ejercicios
@coach_bp.route("/buscar_ejercicios")
def buscar_ejercicios():
    q = request.args.get("q", "").lower()

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT nombre FROM ejercicios_base
            WHERE LOWER(nombre) LIKE %s
            LIMIT 10
        """, (f"%{q}%",))

        resultados = [r[0] for r in cur.fetchall()]
        return {"resultados": resultados}
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

@coach_bp.route("/eliminar_ejercicio", methods=["POST"])
def eliminar_ejercicio():
    if "user_id" not in session:
        return redirect("/")

    ejercicio_id = request.form["id"]

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Obtener rutina a la que pertenece
        cur.execute("SELECT rutina_id FROM ejercicios WHERE id = %s", (ejercicio_id,))
        rutina_id = cur.fetchone()[0]

        # Eliminar ejercicio
        cur.execute("DELETE FROM ejercicios WHERE id = %s", (ejercicio_id,))
        conn.commit()

        return redirect(f"/editar_rutina/{rutina_id}")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

@coach_bp.route("/editar_ejercicio/<int:ejercicio_id>", methods=["GET", "POST"])
def editar_ejercicio(ejercicio_id):
    if "user_id" not in session:
        return redirect("/")

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":
        dia = request.form["dia"]
        nombre = request.form["nombre"]
        series = request.form["series"]
        repeticiones = request.form["repeticiones"]
        peso = request.form["peso"]
        notas = request.form["notas"]

        try:
            cur.execute("""
                UPDATE ejercicios
                SET dia=%s, nombre=%s, series=%s, repeticiones=%s, peso_sugerido=%s, notas=%s
                WHERE id=%s
            """, (dia, nombre, series, repeticiones, peso, notas, ejercicio_id))

            conn.commit()

            # Obtener rutina para redirigir
            cur.execute("SELECT rutina_id FROM ejercicios WHERE id = %s", (ejercicio_id,))
            rutina_id = cur.fetchone()[0]

            return redirect(f"/editar_rutina/{rutina_id}")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    try:
        # Obtener datos del ejercicio para mostrar en el formulario
        cur.execute("""
            SELECT rutina_id, dia, nombre, series, repeticiones, peso_sugerido, notas
            FROM ejercicios
            WHERE id=%s
        """, (ejercicio_id,))

        ejercicio = cur.fetchone()

        return render_template("coach/editar_ejercicio.html", ejercicio=ejercicio)
    finally:
        cur.close()
        conn.close()

@coach_bp.route("/actualizar_ejercicio", methods=["POST"])
def actualizar_ejercicio():
    if "user_id" not in session:
        return {"status": "error", "msg": "No autorizado"}, 403

    data = request.get_json()
    ejercicio_id = data["id"]
    campo = data["campo"]
    valor = data["valor"]

    campos_validos = ["nombre", "series", "repeticiones", "peso_sugerido", "notas"]
    if campo not in campos_validos:
        return {"status": "error", "msg": "Campo inválido"}, 400

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        query = f"UPDATE ejercicios SET {campo} = %s WHERE id = %s"
        cur.execute(query, (valor, ejercicio_id))
        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "msg": str(e)}, 500
    finally:
        cur.close()
        conn.close()

# LISTADO DE RUTINAS
@coach_bp.route("/mis_rutinas")
def mis_rutinas():
    if "user_id" not in session:
        return redirect("/")
    
    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, nombre, objetivo, fecha_creacion
            FROM rutinas
            WHERE profesional_id = %s
            ORDER BY fecha_creacion DESC
        """, (session["user_id"],))
        rutinas = cur.fetchall()
        return render_template("coach/mis_rutinas.html", rutinas=rutinas)
    finally:
        cur.close()
        conn.close()

@coach_bp.route("/eliminar_rutina/<int:rutina_id>", methods=["POST"])
def eliminar_rutina(rutina_id):
    if "user_id" not in session:
        return redirect("/")

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        # 1. Borrar ejercicios de esa rutina
        cur.execute("DELETE FROM ejercicios WHERE rutina_id = %s", (rutina_id,))
        
        # 2. Borrar asignaciones en rutinas_asignadas
        cur.execute("DELETE FROM rutinas_asignadas WHERE rutina_id = %s", (rutina_id,))
        
        # 3. Borrar la rutina
        cur.execute("DELETE FROM rutinas WHERE id = %s", (rutina_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
    
    return redirect("/mis_rutinas")

# REGISTRO DE USUARIOS POR EL COACH
@coach_bp.route("/registro_usuario", methods=["GET", "POST"])
def registro_usuario():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        sexo = request.form["sexo"]
        edad = request.form["edad"]
        peso = request.form["peso"]
        altura = request.form["altura"]
        telefono = request.form["telefono"]

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        from app.db import get_conn
        conn = get_conn()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, contraseña, rol, creado_por_entrenador, sexo, edad, peso, altura, telefono)
                VALUES (%s, %s, %s, 'cliente', true, %s, %s, %s, %s, %s)
                RETURNING id
            """, (nombre, correo, hashed_password, sexo, edad, peso, altura, telefono))
            
            nuevo_usuario_id = cur.fetchone()[0]

            # Asignar automáticamente al coach que lo creó
            cur.execute("""
                INSERT INTO asignaciones (profesional_id, cliente_id)
                VALUES (%s, %s)
            """, (session["user_id"], nuevo_usuario_id))

            conn.commit()
            return redirect("/mis_clientes")
        except Exception as e:
            conn.rollback()
            return f"Error: {e}"
        finally:
            cur.close()
            conn.close()

    return render_template("coach/registro_usuario.html")

# VER USUARIOS CON RUTINA ASIGNADA
@coach_bp.route("/usuarios_asignados")
def usuarios_asignados():
    if "user_id" not in session:
        return redirect("/")

    from app.db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Consulta para ver qué usuarios tienen qué rutina asignada
        cur.execute("""
            SELECT 
                u.nombre AS usuario,
                r.nombre AS rutina,
                u.id AS usuario_id,
                r.id AS rutina_id
            FROM rutinas_asignadas ra
            JOIN usuarios u ON u.id = ra.cliente_id
            JOIN rutinas r ON r.id = ra.rutina_id
            WHERE r.profesional_id = %s
        """, (session["user_id"],))
        
        asignaciones = cur.fetchall()
        return render_template("coach/usuarios_asignados.html", asignaciones=asignaciones)
    finally:
        cur.close()
        conn.close()
