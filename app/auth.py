from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager
from app.models import User
from app.roles import UserRole

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):

            
            print("DEBUG ROLE:", user.role)  # Add this line
            login_user(user)
            flash('Login successful.', 'success')

            if user and check_password_hash(user.password_hash, password):


                # Redirect user based on their role
                if user.role == UserRole.CONTRACTOR:
                    return redirect(url_for('routes.contractor_home'))
                elif user.role == UserRole.MANAGER:
                    return redirect(url_for('routes.home'))
                elif user.role == UserRole.ADMIN:
                    return redirect(url_for('routes.admin_dashboard'))
                else:
                    flash(f'Unknown user role: {user.role}', 'danger')
                    return redirect(url_for('auth.login'))

        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != UserRole.ADMIN:
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Optional: normalize role input
        if role.upper() == "CONTRACTOR":
            role = UserRole.CONTRACTOR
        elif role.upper() == "MANAGER":
            role = UserRole.MANAGER
        else:
            role = UserRole.ADMIN

        hashed_password = generate_password_hash(password)

        user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()

        flash("User registered successfully.", "success")
        return redirect(url_for('routes.home'))

    return render_template('register.html')

