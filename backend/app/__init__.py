"""Application factory for the Location-Aware Campus Portal backend."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from .models import db

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_object: str = "config.Config") -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_object)

    db.init_app(app)
    CORS(app)  # allows the captive-portal page to call the API during dev

    from .api import api

    app.register_blueprint(api)

    # Serve the captive-portal frontend so a single process serves both the
    # landing page and the API — convenient for local runs and for a gateway.
    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:filename>")
    def frontend_files(filename: str):
        return send_from_directory(FRONTEND_DIR, filename)

    with app.app_context():
        db.create_all()

    return app
