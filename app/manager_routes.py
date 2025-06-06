from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import permission_required, role_required
from app.models import db, WorkOrder, Client, User, Role, BusinessType

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
        client_id = request.form['client_id']
        created_by = current_user.full_name or current_user.email

        new_order = WorkOrder(
            title=title,
            description=description,
            client_id=client_id,
            created_by=created_by,
            status='Open'
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Work order created successfully.', 'success')
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
# View Single Work Order (optional)
# ----------------------
@manager_routes_bp.route('/manager/work-orders/<int:order_id>')
@login_required
@permission_required("view_work_order")
def view_work_order(order_id):
    work_order = WorkOrder.query.get_or_404(order_id)
    return render_template('work_orders/view_work_order.html', work_order=work_order)

# ----------------------
# Edit Work Order (optional)
# ----------------------
@manager_routes_bp.route('/manager/work-orders/update/<int:order_id>', methods=['POST'], endpoint='update_work_order')
@login_required
@permission_required("edit_work_order")
def update_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    
    # Get new data from form
    order.title = request.form.get('title')
    order.description = request.form.get('description')
    order.status = request.form.get('status')
    order.priority = request.form.get('priority')
    
    db.session.commit()
    flash("Work order updated successfully.", "success")
    return redirect(url_for('manager_routes.view_all_work_orders'))

