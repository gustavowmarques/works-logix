from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import permission_required, role_required
from app.models import db, WorkOrder, Client, User, Role, BusinessType
from app.shared_routes import shared_routes_bp
from datetime import datetime


manager_routes_bp = Blueprint('manager_routes', __name__)

# ----------------------
# Manager Home Dashboard
# ----------------------
@manager_routes_bp.route('/manager/home')
@login_required
@permission_required("view_manager_home")
def manager_home():
    work_orders = WorkOrder.query.all()
    return render_template("manager/home.html", work_orders=work_orders)

# ----------------------
# Create Work Order
# ----------------------
@manager_routes_bp.route('/manager/work-orders/create', methods=['GET', 'POST'])
@login_required
@role_required(['Property Manager', 'Admin']) 
@permission_required("create_work_order")
def create_work_order():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if not title:
            flash('Title is required.', 'danger')
            return redirect(request.url)

        if not description:
            flash('Description is required.', 'danger')
            return redirect(request.url)


        client_id = request.form['client_id']
        business_type = request.form.get('business_type')
        preferred_contractor_id = request.form.get('preferred_contractor_id') or None
        second_preferred_contractor_id = request.form.get('second_preferred_contractor_id') or None

        occupant_apartment = request.form.get('occupant_apartment') or ''
        occupant_name = request.form.get('occupant_name') or ''
        occupant_phone = request.form.get('occupant_phone') or ''

        created_by = current_user.full_name or current_user.email

        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

        new_order = WorkOrder(
            title=title,
            description=description,
            client_id=client_id,
            business_type=business_type,
            preferred_contractor_id=preferred_contractor_id,
            second_preferred_contractor_id=second_preferred_contractor_id,
            occupant_apartment=occupant_apartment,
            occupant_name=occupant_name,
            occupant_phone=occupant_phone,
            created_by=created_by,
            due_date=due_date,
            status='Open'
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Work order created successfully.', 'success')
        
        if current_user.role.name == "Admin":
            return redirect(url_for('admin_routes.admin_dashboard')) 
        else:
            return redirect(url_for('manager_routes.manager_home'))
    
    # Fetch dropdown values
    if current_user.role.name == 'Admin':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(assigned_property_manager_id=current_user.id).all()

    contractors = User.query.filter(User.role.has(name='Contractor')).all()
    contractor_categories = list({c.business_type.name for c in contractors if c.business_type})

    return render_template(
        'work_orders/create_work_order.html',
        clients=clients,
        contractors=contractors,
        contractor_categories=contractor_categories,
        order=None
    )

# ----------------------
# View All Work Orders
# ----------------------
@manager_routes_bp.route('/manager/work-orders', methods=['GET'], endpoint='view_all_work_orders')
@login_required
@permission_required("view_work_order")
def view_all_work_orders():
    work_orders = WorkOrder.query.all()
    return render_template('manager/view_all_work_orders.html', work_orders=work_orders)

# ----------------------
# View A Single Work Order
# ----------------------
@manager_routes_bp.route('/manager/work-orders/<int:order_id>', methods=['GET'], endpoint='view_work_order')
@login_required
@permission_required("view_work_order")
def view_work_order(order_id):
    work_order = WorkOrder.query.get_or_404(order_id)
    return render_template('manager/view_work_order.html', work_order=work_order)

