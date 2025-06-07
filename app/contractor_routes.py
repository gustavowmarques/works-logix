from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.decorators import permission_required, role_required
from app.models import db, WorkOrder


contractor_routes_bp = Blueprint('contractor_routes', __name__)

@contractor_routes_bp.route('/contractor/home')
@login_required
@role_required(['Contractor'])
@permission_required('contractor_home')
def contractor_home():
    work_orders = WorkOrder.query.filter_by(contractor_id=current_user.id).all()
    return render_template('contractor/contractor_home.html', work_orders=work_orders)

@contractor_routes_bp.route('/contractor/reject/<int:order_id>', methods=['POST'])
@login_required
@permission_required("reject_work_order")
def reject_work_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    if order.contractor_id != current_user.id:
        abort(403)
    order.status = 'Rejected'
    db.session.commit()
    flash('Work order rejected.', 'info')
    return redirect(url_for('contractor.contractor_home'))

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