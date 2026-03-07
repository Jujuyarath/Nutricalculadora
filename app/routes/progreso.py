from flask import Blueprint, request, jsonify
from app import db
from app.models import Progreso

progreso_bp = Blueprint('progreso', __name__)

from app.utils.auth import token_required

@progreso_bp.route('/api/progreso', methods=['POST'])
@token_required
def crear_progreso(usuario_actual):
    data = request.json

    nuevo = Progreso(
        cliente_id=usuario_actual,
        rutina_id=data.get('rutina_id'),
        ejercicio_id=data.get('ejercicio_id'),
        series_realizada=data.get('series_realizada'),
        reps_realizadas=data.get('reps_realizadas'),
        peso_realizado=data.get('peso_realizado'),
        notas_cliente=data.get('notas_cliente')
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"mensaje": "Progreso guardado", "id": nuevo.id}), 201

@progreso_bp.route('/api/progreso/cliente', methods=['GET'])
@token_required
def progreso_por_cliente(usuario_actual):
    registros = Progreso.query.filter_by(cliente_id=usuario_actual).all()

    resultado = [
        {
            "id": r.id,
            "rutina_id": r.rutina_id,
            "ejercicio_id": r.ejercicio_id,
            "fecha": r.fecha,
            "series_realizadas": r.series_realizada,
            "reps_realizadas": r.reps_realizadas,
            "peso_realizado": r.peso_realizado,
            "notas_cliente": r.notas_cliente
        }
        for r in registros
    ]

    return jsonify(resultado), 200