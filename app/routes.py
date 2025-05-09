from flask import render_template, request, redirect, url_for, flash, abort
from .models import WorkOrder, Client, Contractor
from flask import current_app as app
from flask_login import login_required, current_user
from . import db

@app.route('/')
def root():
    return redirect(url_for('login'))  # Default landing page

@app.route('/home')
@login_required
def home():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('home.html', orders=orders)

@app.route('/register-client', methods=['GET', 'POST'])
@login_required
def register_client():
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        registration_number = request.form['registration_number']
        year_built = request.form['year_built']
        number_of_units = request.form['number_of_units']

        new_client = Client(
            name=name,
            address=address,
            registration_number=registration_number,
            year_built=year_built,
            number_of_units=number_of_units
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client registered successfully.')
        return redirect(url_for('register_client'))

    return render_template('register_client.html')

@app.route('/work-orders')
@login_required
def work_orders():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('work_orders.html', orders=orders)

@app.route('/work-orders/create', methods=['GET', 'POST'])
@login_required
def create_work_order():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        created_by = current_user.username  # Prefer using session info
        client_id = request.form['client_id']
        contractor_id = request.form['contractor_id']

        new_order = WorkOrder(
            title=title,
            description=description,
            created_by=created_by,
            client_id=client_id,
            contractor_id=contractor_id
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Work order created successfully.')
        return redirect(url_for('home'))

    # Handle GET – load dropdown options
    clients = Client.query.all()
    contractors = Contractor.query.all()
    return render_template('partials/create_work_order.html', clients=clients, contractors=contractors)


