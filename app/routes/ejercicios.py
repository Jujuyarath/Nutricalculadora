from flask import Blueprint, jsonify
from app.models import Ejercicios
from app.utils.auth import token_required

ejercicios_bp = Blueprint('ejercicios', __name__)

@ejercicios_bp.route('/api/ejercicios', methods=['GET'])
@token_required
def obtener_ejercicios(usuario_actual):
    ejercicios = Ejercicios.query.all()

    resultado = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "rutina_id": e.rutina_id,
            "series": e.series,
            "repeticiones": e.repeticiones,
            "peso_sugerido": e.peso_sugerido,
            "notas": e.notas,
            "dia": e.dia
        }
        for e in ejercicios
    ]

    return jsonify(resultado), 200