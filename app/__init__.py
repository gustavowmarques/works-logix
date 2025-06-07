from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager
from app.roles import UserRole

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app import models
        from app.models import User, Client, Role, RolePermission

    # Register blueprints
    from app.auth import auth_bp
    from app.admin_routes import admin_routes_bp
    from app.manager_routes import manager_routes_bp
    from app.contractor_routes import contractor_routes_bp
    from app.routes import main_bp
    from app.shared_routes import shared_routes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_routes_bp)
    app.register_blueprint(manager_routes_bp)
    app.register_blueprint(contractor_routes_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(shared_routes_bp)

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
