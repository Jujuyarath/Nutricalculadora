import os
from app import create_app

try:
    app = create_app()
except Exception as e:
    print("ERROR AL CREAR LA APP:", e)
    raise e

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)