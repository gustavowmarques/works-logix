from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from app.roles import UserRole

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

    migrate = Migrate()
    migrate.init_app(app, db)

    with app.app_context():
        from . import routes, models, auth
        db.create_all()

    @app.context_processor
    def inject_roles():
        return {
            'ROLE_ADMIN': UserRole.ADMIN.value,
            'ROLE_MANAGER': UserRole.MANAGER.value,
            'ROLE_CONTRACTOR': UserRole.CONTRACTOR.value
        }

    return app
