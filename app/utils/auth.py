import jwt
import datetime
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "sdkjbñepootiy3bn2854nflkijf43v3897gpc89m28p09ol2w9ir46930202007"

def generar_token(usuario_id):
    payload = {
        "usuario_id": usuario_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verificar_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data["usuario_id"]
    except:
        return None
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token requerido"}), 401
        
        usuario_id = verificar_token(token)
        if not usuario_id:
            return jsonify({"error": "Token inválido o expirado"}), 401
        
        return f(usuario_id, *args, **kwargs)
    
    return decorated