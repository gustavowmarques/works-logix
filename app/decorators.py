from functools import wraps
from flask import session, flash, redirect, url_for
from app.models import Role, RolePermission
from app import db
from flask_login import current_user
from sqlalchemy import func

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Unauthorized access.", "danger")
                return redirect(url_for("auth.unauthorized"))

            user_role = current_user.role.name

            if user_role.strip().lower() == "admin":
                return f(*args, **kwargs)

            role = db.session.query(Role).filter(func.lower(Role.name) == user_role.lower()).first()
            if not role:
                flash("Role not found.", "danger")
                return redirect(url_for("auth.unauthorized"))

            permission_obj = db.session.query(RolePermission).filter_by(
                role_id=role.id, permission=permission
            ).first()

            if not permission_obj:
                flash("You do not have permission to access this page.", "warning")
                return redirect(url_for("auth.unauthorized"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "warning")
                return redirect(url_for("auth.login"))

            user_role = current_user.role.name.strip().lower()
            allowed_roles = [r.lower() for r in roles]

            print(f"[DEBUG] Required roles: {allowed_roles}, Current role: {user_role}")  # Optional debug

            if user_role not in allowed_roles:
                flash("You do not have access to this resource.", "danger")
                return redirect(url_for("auth.unauthorized"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

