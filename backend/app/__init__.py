import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

db = SQLAlchemy()
jwt = JWTManager()


def database_url(url=None):
    vrednost = url if url is not None else os.environ["DATABASE_URL"]
    if vrednost.startswith("postgresql+psycopg://") or vrednost.startswith("postgresql+psycopg2://"):
        return vrednost
    if vrednost.startswith("postgresql://"):
        return "postgresql+psycopg://" + vrednost[len("postgresql://") :]
    if vrednost.startswith("postgres://"):
        return "postgresql+psycopg://" + vrednost[len("postgres://") :]
    return vrednost


def cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=cors_origins())

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    from app import models  # noqa: F401
    from app.kuhinja import bp as kuhinja_bp
    from app.narocila import bp as narocila_bp
    from app.prijava import bp as prijava_bp
    from app.racuni import bp as racuni_bp
    from app.rezervacije import bp as rezervacije_bp
    from app.zaloge import bp as zaloge_bp

    app.register_blueprint(kuhinja_bp)
    app.register_blueprint(narocila_bp)
    app.register_blueprint(prijava_bp)
    app.register_blueprint(racuni_bp)
    app.register_blueprint(rezervacije_bp)
    app.register_blueprint(zaloge_bp)
    return app
