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
            "grupo_muscular": e.grupo_muscular,
            "descripcion": e.descripcion
        }
        for e in ejercicios
    ]

    return jsonify(resultado), 200