from flask import Blueprint, request, jsonify
from app.utils.db import db
from app.utils.models import Progreso

progreso_bp = Blueprint('progreso', __name__)

@progreso_bp.route('/progreso', methods=['POST'])
def crear_progreso():
    data = request.json

    nuevo = Progreso(
        cliente_id=data.get('cliente_id'),
        rutina_id=data.get('rutina_id'),
        ejercicio_id=data.get('ejercicio_id'),
        series_realizadas=data.get('series_realizadas'),
        reps_realizadas=data.get('reps_realizadas'),
        peso_realizado=data.get('peso_realizado'),
        notas_cliente=data.get('notas_cliente')
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"mensaje": "Progreso guardado", "id": nuevo.id}), 201

@progreso_bp.route('/progreso/cliente/<int:cliente_id>', methods=['GET'])
def progreso_por_cliente(cliente_id):
    registros = Progreso.query.filter_by(cliente_id=cliente_id).all()

    resultado = [
        {
            "id": r.id,
            "rutina_id": r.rutina_id,
            "ejercicio_id": r.ejercicio_id,
            "fecha": r.fecha,
            "series_realizadas": r.series_realizadas,
            "reps_realizadas": r.reps_realizadas,
            "peso_realizado": r.peso_realizado,
            "notas_cliente": r.notas_cliente
        }
        for r in registros
    ]

    return jsonify(resultado), 200