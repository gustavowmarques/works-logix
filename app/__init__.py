from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.roles import UserRole
from app.routes import main_bp
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    with app.app_context():
        from app import models

    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import ALL models early so they're registered with SQLAlchemy's metadata
    from app.models import User, Client, Role, RolePermission

    # Register blueprints
    from app.auth import auth_bp
    from app.admin_routes import admin_routes_bp
    from app.manager_routes import manager_routes_bp
    from app.contractor_routes import contractor_routes_bp
    from app.routes import main_bp  # You were missing this import!

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_routes_bp)
    app.register_blueprint(manager_routes_bp)
    app.register_blueprint(contractor_routes_bp)
    app.register_blueprint(main_bp)

    # Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Inject role constants into templates
    @app.context_processor
    def inject_roles():
        return {
            'ROLE_ADMIN': UserRole.ADMIN.value,
            'ROLE_MANAGER': UserRole.MANAGER.value,
            'ROLE_CONTRACTOR': UserRole.CONTRACTOR.value
        }

    return app
