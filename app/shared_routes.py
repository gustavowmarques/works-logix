from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import WorkOrder
from app.decorators import permission_required

shared_routes_bp = Blueprint('shared_routes', __name__)

@shared_routes_bp.route('/work-orders/update/<int:order_id>', methods=['GET', 'POST'], endpoint='update_work_order')
@login_required
@permission_required("edit_work_order")
def update_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)

    if request.method == 'POST':
        order.title = request.form.get('title')
        order.description = request.form.get('description')
        order.status = request.form.get('status')
        order.priority = request.form.get('priority')
        db.session.commit()
        flash("Work order updated successfully.", "success")
        return redirect(url_for('admin.admin_work_orders'))  # Or 'manager_routes.view_all_work_orders'

    return render_template('shared/edit_work_order.html', work_order=order)
