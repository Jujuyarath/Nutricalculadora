from flask import Blueprint, jsonify
from app import db
from app.models import Rutina, RutinasAsignadas
from app.utils.auth import token_required

rutinas_bp = Blueprint('rutinas', __name__)

@rutinas_bp.route('/api/rutinas', methods=['GET'])
@token_required
def obtener_rutinas(usuario_actual):

    rutinas = (
        db.session.query(Rutina)
        .join(RutinasAsignadas, RutinasAsignadas.rutina_id == Rutina.id)
        .filter(RutinasAsignadas.cliente_id == usuario_actual)
        .all()
    )

    resultado = [
        {
            "id": r.id,
            "nombre": r.nombre,
            "objetivo": r.objetivo,
            "fecha_creacion": r.fecha_creacion
        }
        for r in rutinas
    ]

    return jsonify(resultado), 200