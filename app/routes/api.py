from flask import Blueprint, request, jsonify
from app.utils.grasa import calcular_medidas
from app.db import get_conn

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 1) OBTENER RUTINA DEL DÍA (corregido: buscar vía rutinas_asignadas)
@api_bp.route("/rutina/<int:usuario_id>/<dia>", methods=["GET"])
def obtener_rutina(usuario_id, dia):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT e.id, e.nombre, e.series, e.repeticiones, e.peso_sugerido, e.notas
            FROM ejercicios e
            JOIN rutinas_asignadas ra ON ra.rutina_id = e.rutina_id
            WHERE ra.cliente_id = %s AND e.dia = %s
        """, (usuario_id, dia))

        ejercicios = cur.fetchall()

        data = [
            {
                "id": e[0],
                "nombre": e[1],
                "series": e[2],
                "repeticiones": e[3],
                "peso": e[4],
                "notas": e[5],
            }
            for e in ejercicios
        ]

        return jsonify({"dia": dia, "ejercicios": data})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# 2) REGISTRAR TIEMPO DE RUTINA
@api_bp.route("/tiempo", methods=["POST"])
def registrar_tiempo():
    try:
        data = request.json

        usuario_id = data["usuario_id"]
        dia = data["dia"]
        tiempo = data["tiempo"]

        conn = get_conn()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO tiempos (usuario_id, dia, tiempo)
                VALUES (%s, %s, %s)
            """, (usuario_id, dia, tiempo))

            conn.commit()

            return jsonify({"status": "ok"})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3) REGISTRAR MEDIDAS
@api_bp.route("/medidas", methods=["POST"])
def registrar_medidas_api():
    try:
        data = request.json

        sexo = data["sexo"]
        peso = float(data["peso"])
        altura = float(data["altura"])
        cuello = float(data["cuello"])

        if sexo == "M":
            abdomen = float(data["abdomen"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, abdomen=abdomen)
        else:
            cintura = float(data["cintura"])
            cadera = float(data["cadera"])
            resultado = calcular_medidas(sexo, peso, altura, cuello, cintura=cintura, cadera=cadera)

        conn = get_conn()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO historial (usuario_id, grasa, masa_muscular, imc, whtr)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["usuario_id"],
                resultado["grasa"],
                resultado["masa_muscular"],
                resultado["imc"],
                resultado["whtr"]
            ))

            conn.commit()

            return jsonify(resultado)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4) OBTENER PROGRESO POR DÍA
@api_bp.route("/progreso/<int:usuario_id>/<dia>", methods=["GET"])
def obtener_progreso(usuario_id, dia):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT tiempo
            FROM tiempos
            WHERE usuario_id = %s AND dia = %s
            ORDER BY id DESC
            LIMIT 1
        """, (usuario_id, dia))

        row = cur.fetchone()

        return jsonify({"dia": dia, "tiempo": row[0] if row else 0})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# 5) OBTENER HISTORIAL DE MEDIDAS CORPORALES
@api_bp.route("/historial/<int:usuario_id>", methods=["GET"])
def obtener_historial(usuario_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, grasa, masa_muscular, imc, whtr, fecha
            FROM historial
            WHERE usuario_id = %s
            ORDER BY fecha DESC
        """, (usuario_id,))

        rows = cur.fetchall()

        data = [
            {
                "id": r[0],
                "grasa": float(r[1]) if r[1] else 0,
                "masa_muscular": float(r[2]) if r[2] else 0,
                "imc": float(r[3]) if r[3] else 0,
                "whtr": float(r[4]) if r[4] else 0,
                "fecha": str(r[5]) if r[5] else "",
            }
            for r in rows
        ]

        return jsonify(data)
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()