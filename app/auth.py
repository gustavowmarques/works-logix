from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager
from app.models import User
from app.roles import UserRole
from app.decorators import permission_required


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        print("Login attempt:", repr(email), repr(password))

        user = User.query.filter_by(email=email).first()

        if not user:
            print("No user found for:", email)
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        print("Found user:", user.email)
        print("Hash in DB:", user.password_hash)
        print("Password check result:", check_password_hash(user.password_hash, password))

        if check_password_hash(user.password_hash, password):
            if user.role is None:
                flash('Your account has no role assigned. Please contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user)
            session['role'] = user.role.name

            flash('Login successful.', 'success')

            role_name = user.role.name.lower()

            if role_name == 'admin':
                return redirect(url_for('admin_routes.admin_dashboard'))
            elif role_name == 'property manager':
                return redirect(url_for('manager_routes.manager_home'))
            elif role_name == 'contractor':
                return redirect(url_for('contractor_routes.contractor_home'))
            else:
                flash('Unknown role. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))


        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/unauthorized')
def unauthorized():
    return render_template('auth/unauthorized.html'), 403

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@permission_required("create_user") 
def register():
    if current_user.role != UserRole.ADMIN:
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role_str = request.form.get('role')

        # Convert form role string to Enum safely
        try:
            role_enum = UserRole(role_str)
        except ValueError:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('auth.register'))

        business_type = request.form.get('business_type') if role_enum == UserRole.CONTRACTOR else None

        new_user = User(
            username=username,
            email=email,
            role=role_enum,
            business_type=business_type,
            password_hash=generate_password_hash(password)
        )

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('routes.register'))

        db.session.add(new_user)
        db.session.commit()

        flash("User registered successfully.", "success")
        return redirect(url_for('routes.home'))

    return render_template('register.html')


