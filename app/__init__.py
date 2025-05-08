from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes, models, auth  # make sure auth.py exists
        db.create_all()

    return app