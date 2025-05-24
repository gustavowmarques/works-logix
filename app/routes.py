from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import WorkOrder, Client, Contractor, WorkOrderStatus, User
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
    return redirect(url_for('routes.home'))


@routes_bp.route('/work-orders/create', methods=['GET', 'POST'])
@login_required
def create_work_order():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        created_by = current_user.username  # Prefer using session info
        client_id = request.form['client_id']
        contractor_id = request.form['contractor_id']
        occupant_apartment = request.form.get('occupant_apartment')
        occupant_contact = request.form.get('occupant_contact')
        business_type = request.form['business_type']
        preferred_contractor_id = request.form.get('preferred_contractor_id') or None


        new_order = WorkOrder(
            title=title,
            description=description,
            created_by=current_user.username,
            status="Open",
            client_id=client_id,
            business_type=business_type,
            preferred_contractor_id=preferred_contractor_id,
            contractor_id=contractor_id,
            occupant_apartment=occupant_apartment,
            occupant_contact=occupant_contact
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Work order created successfully.')
        return redirect(url_for('routes.home'))

    # Handle GET – load dropdown options
    clients = Client.query.all()
    contractors = User.query.filter_by(role=UserRole.CONTRACTOR).all()
    return render_template('partials/create_work_order.html', clients=clients, contractors=contractors)

@routes_bp.route('/contractor/work-orders')
@login_required
def contractor_work_orders():
    if current_user.role not in [UserRole.CONTRACTOR, UserRole.ADMIN]:
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
    if current_user.role not in [UserRole.CONTRACTOR, UserRole.ADMIN]:
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
    if current_user.role not in [UserRole.CONTRACTOR, UserRole.ADMIN]:
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
    if current_user.role not in [UserRole.CONTRACTOR, UserRole.ADMIN]:
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


@routes_bp.route('/work-orders/<int:order_id>/reopen', methods=['POST'])
@login_required
def reopen_work_order(order_id):
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        abort(403)

    order = WorkOrder.query.get_or_404(order_id)

    if order.status != 'Completed':
        flash("Only completed work orders can be reopened.", "warning")
        return redirect(url_for('routes.work_order_detail', order_id=order.id))

    order.status = 'Open'
    order.contractor_id = None
    order.completion_photo = None
    db.session.commit()
    flash("Work order has been reopened.", "success")
    return redirect(url_for('routes.work_order_detail', order_id=order.id))

@routes_bp.route('/work-orders/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_work_order(order_id):
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        abort(403)

    order = WorkOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash("Work order deleted successfully.", "success")
    return redirect(url_for('routes.work_orders'))


@routes_bp.route('/work-orders/<int:order_id>')
@login_required
def work_order_detail(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    return render_template('work_order_detail.html', order=order)

@routes_bp.route('/clients/<int:client_id>')
@login_required
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('client_detail.html', client=client)

@routes_bp.route('/contractors/<int:contractor_id>')
@login_required
def contractor_detail(contractor_id):
    contractor = User.query.get_or_404(contractor_id)
    return render_template('contractor_detail.html', contractor=contractor)

@routes_bp.route('/contractor/home')
@login_required
def contractor_home():
    contractor = User.query.get(current_user.id)

    # Orders already accepted by this contractor
    assigned_orders = WorkOrder.query.filter_by(contractor_id=contractor.id).all()

    # Orders only for this contractor as preferred and still Open
    preferred_orders = WorkOrder.query.filter_by(
        status='Open',
        preferred_contractor_id=contractor.id,
        contractor_id=None
    ).all()

    # Fallback orders if preferred contractor has rejected and this contractor hasn't
    eligible_orders = WorkOrder.query.filter(
        WorkOrder.status == 'Open',
        WorkOrder.contractor_id.is_(None),
        WorkOrder.business_type == contractor.business_type,
        WorkOrder.preferred_contractor_id.is_(None),
        ~WorkOrder.rejected_by.contains(str(contractor.id))
    ).all()

    return render_template(
        'contractor_home.html',
        assigned_orders=assigned_orders,
        preferred_orders=preferred_orders,
        eligible_orders=eligible_orders
    )


@routes_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != UserRole.ADMIN:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('auth.login'))

    return render_template('admin_dashboard.html')

@routes_bp.route('/admin/users')
@login_required
def view_all_users():
    if current_user.role != UserRole.ADMIN:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))
    return "<h2>Coming soon: User list</h2>"

@routes_bp.route('/admin/clients')
@login_required
def view_all_clients():
    if current_user.role != UserRole.ADMIN:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))
    return "<h2>Coming soon: Client list</h2>"

@routes_bp.route('/admin/contractors')
@login_required
def view_all_contractors():
    if current_user.role != UserRole.ADMIN:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))
    return "<h2>Coming soon: Contractor list</h2>"
