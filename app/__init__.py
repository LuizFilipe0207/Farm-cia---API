from flask import Flask
from .database import init_db
from .routers.medicamentos import medicamentos_bp
from .routers.estoque import estoque_bp


def create_app():
    app = Flask(__name__)

    init_db()

    app.register_blueprint(medicamentos_bp, url_prefix="/api/medicamentos")
    app.register_blueprint(estoque_bp, url_prefix="/api/estoque")

    return app
