from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
