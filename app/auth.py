
from flask import render_template, redirect, url_for, flash, request, abort, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Contractor
from . import db
from .roles import UserRole
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful.')
            return redirect(url_for('home'))  # or another route you prefer

        flash('Invalid email or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from .models import User
    user_count = User.query.count()

    # Safe role check to avoid AttributeError
    if user_count > 0 and (not current_user.is_authenticated or current_user.role != 'ROLE_ADMIN'):
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if role == 'manager':
            role = ROLE_MANAGER

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)

        if role == ROLE_CONTRACTOR:
            company_name = request.form['company_name']
            company_registration_number = request.form['company_registration_number']
            telephone = request.form['telephone']
            accounts_contact_name = request.form['accounts_contact_name']
            accounts_contact_email = request.form['accounts_contact_email']
            contractor_address = request.form['contractor_address']
            business_type = request.form['business_type']

            contractor = Contractor(
                company_name=company_name,
                company_registration_number=company_registration_number,
                email=email,
                telephone=telephone,
                accounts_contact_name=accounts_contact_name,
                accounts_contact_email=accounts_contact_email,
                address=contractor_address,
                business_type=business_type
            )
            db.session.add(contractor)

        db.session.commit()
        flash('Registration successful. You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))
