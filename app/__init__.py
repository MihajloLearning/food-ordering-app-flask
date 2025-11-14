import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("No DATABASE_URL set for Flask application")
    
    # Heroku/Render use postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from . import routes
        # routes.register_routes(app) # This line is not needed as routes are registered via blueprints
        db.create_all()

    return app