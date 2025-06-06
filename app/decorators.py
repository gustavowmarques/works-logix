from functools import wraps
from flask import session, flash, redirect, url_for
from app.models import Role, RolePermission
from flask_login import current_user

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app import db
            from app.models import Role, RolePermission
            from sqlalchemy import func

            user_role = session.get("role")
            if not user_role:
                flash("Unauthorized access.", "danger")
                return redirect(url_for("auth.unauthorized"))

            # Allow Admins to bypass
            if user_role.lower() == "admin":
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
            if current_user.role and current_user.role.name in roles:
                return f(*args, **kwargs)
            flash("You do not have access to this resource.", "danger")
            return redirect(url_for("auth.login"))
        return decorated_function
    return decorator
