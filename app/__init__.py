from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from app.extensions import db, login_manager, migrate
from config import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from app.roles import UserRole
from . import auth
from app.routes import routes_bp
from app.auth import auth_bp
from app.models import User


login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Register Blueprints
    from app.routes import routes_bp
    from app.auth import auth_bp
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)

    # Inject roles into templates
    @app.context_processor
    def inject_roles():
        return {
            'ROLE_ADMIN': UserRole.ADMIN.value,
            'ROLE_MANAGER': UserRole.MANAGER.value,
            'ROLE_CONTRACTOR': UserRole.CONTRACTOR.value
        }

    @app.context_processor
    def inject_roles():
        return {
            'ROLE_ADMIN': UserRole.ADMIN.value,
            'ROLE_MANAGER': UserRole.MANAGER.value,
            'ROLE_CONTRACTOR': UserRole.CONTRACTOR.value
        }

    return app
