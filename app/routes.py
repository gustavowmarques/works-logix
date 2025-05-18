from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import WorkOrder, Client, Contractor, WorkOrderStatus
from app.roles import UserRole
from flask import current_app as app
from flask_login import login_required, current_user
from app.extensions import db
from sqlalchemy import or_, and_
import os
from werkzeug.utils import secure_filename

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def root():
    return redirect(url_for('auth.login'))  # Default landing page

@routes_bp.route('/home')
@login_required
def home():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('home.html', orders=orders)

@routes_bp.route('/register-client', methods=['GET', 'POST'])
@login_required
def register_client():
    if current_user.role != UserRole.ADMIN:
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
        flash('Client registered successfully.', 'success')
        return redirect(url_for('routes.register_client'))

    return render_template('register_client.html')



@routes_bp.route('/work-orders')
@login_required
def work_orders():
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        abort(403)

    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('work_orders.html', orders=orders)


@routes_bp.route('/work-orders/create', methods=['GET', 'POST'])
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
        return redirect(url_for('routes.home'))

    # Handle GET – load dropdown options
    clients = Client.query.all()
    contractors = Contractor.query.all()
    return render_template('partials/create_work_order.html', clients=clients, contractors=contractors)

@routes_bp.route('/contractor/work-orders')
@login_required
def contractor_work_orders():
    if current_user.role != UserRole.CONTRACTOR:
        abort(403)

    orders = WorkOrder.query.filter(
        and_(
            or_(
                WorkOrder.contractor_id == None,
                WorkOrder.contractor_id == current_user.id
            ),
            or_(
                WorkOrder.rejected_by == None,
                WorkOrder.rejected_by != current_user.id
            )
        )
    ).order_by(WorkOrder.created_at.desc()).all()

    return render_template('contractor_work_orders.html', orders=orders)

@routes_bp.route('/contractor/work-orders/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_work_order(order_id):
    if current_user.role != UserRole.CONTRACTOR:
        abort(403)
    
    order = WorkOrder.query.get_or_404(order_id)
    
    if order.contractor_id:
        flash("This work order has already been accepted.", "warning")
    else:
        order.contractor_id = current_user.id
        order.status = "Accepted"
        order.rejected_by = None
        db.session.commit()
        flash("You have accepted the work order.", "success")

    return redirect(url_for('routes.contractor_work_orders'))


@routes_bp.route('/contractor/work-orders/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_work_order(order_id):
    if current_user.role != UserRole.CONTRACTOR:
        abort(403)

    order = WorkOrder.query.get_or_404(order_id)
    if order.contractor_id == current_user.id or order.contractor_id is None:
        order.contractor_id = None
        order.status = 'Open'
        order.rejected_by = current_user.id
        db.session.commit()
        flash("Work order rejected.", "info")
    else:
        flash("You can't reject this work order.", "warning")

    return redirect(url_for('routes.contractor_work_orders'))

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

@routes_bp.route('/contractor/work-orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_work_order(order_id):
    if current_user.role != UserRole.CONTRACTOR:
        abort(403)

    order = WorkOrder.query.get_or_404(order_id)
    if order.contractor_id != current_user.id:
        abort(403)

    # Handle file upload
    if 'completion_photo' in request.files:
        file = request.files['completion_photo']
        if file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            order.completion_photo = filename

    order.status = 'Completed'
    db.session.commit()
    flash('Work order marked as completed.', 'success')
    return redirect(url_for('routes.contractor_work_orders'))


@routes_bp.route('/work-orders/reopen/<int:order_id>', methods=['POST'])
@login_required
def reopen_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    if current_user.role != UserRole.MANAGER:
        abort(403)

    order.status = WorkOrderStatus.OPEN
    order.contractor = None
    db.session.commit()
    flash("Work order has been reopened.", "info")
    return redirect(url_for('routes.home'))


