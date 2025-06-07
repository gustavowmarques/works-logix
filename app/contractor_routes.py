from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.decorators import permission_required, role_required
from app.models import db, WorkOrder


contractor_routes_bp = Blueprint('contractor_routes', __name__)

# Define a route for contractor-related operations
@contractor_routes_bp.route('/contractor/home')
@login_required
@role_required(['Contractor'])
@permission_required("view_contractor_dashboard")

# View function for contractor dashboard to show assigned work orders
def contractor_home():
    contractor_id = current_user.id
    orders = WorkOrder.query.filter(
        or_(
            WorkOrder.preferred_contractor_id == contractor_id,
            WorkOrder.contractor_id == contractor_id
        )
    ).all()
    return render_template('contractor/contractor_home.html', orders=orders)

# Define a route for contractor-related operations
@contractor_routes_bp.route('/contractor/reject/<int:order_id>', methods=['POST'])
@login_required
@permission_required("reject_work_order")

# View to handle contractor rejecting a work order
def reject_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    if order.contractor_id != current_user.id:
        abort(403)
    order.status = 'Rejected'
    db.session.commit()
    flash('Work order rejected.', 'info')
    return redirect(url_for('contractor.contractor_home'))

# Define a route for contractor-related operations
@contractor_routes_bp.route('/contractor/complete/<int:order_id>', methods=['POST'])
@login_required
@permission_required("complete_work_order")
def complete_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    if order.contractor_id != current_user.id:
        abort(403)
    order.status = 'Completed'
    db.session.commit()
    flash('Work order marked as completed.', 'success')
    return redirect(url_for('contractor.contractor_home'))

# Define a route for contractor-related operations
@contractor_routes_bp.route('/contractor/work-orders/<int:order_id>', endpoint='view_work_order')
@login_required
@role_required(['Contractor'])
@permission_required("view_contractor_dashboard")
def view_work_order(order_id):
    from app.models import WorkOrder

    work_order = WorkOrder.query.get_or_404(order_id)

    # Optional: check that the contractor has permission to see it
    contractor_id = current_user.id
    if work_order.preferred_contractor_id != contractor_id and work_order.contractor_id != contractor_id:
        flash("You are not authorized to view this work order.", "danger")
        return redirect(url_for('contractor_routes.contractor_home'))

    return render_template('contractor/view_work_order.html', order=work_order)
