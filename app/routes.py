from flask import render_template, request, redirect, url_for
from . import db
from .models import WorkOrder
from flask import current_app as app

@app.route('/')
def home():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('home.html', orders=orders)

@app.route('/work-orders')
def work_orders():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('work_orders.html', orders=orders)

@app.route('/work-orders/create', methods=['POST'])
def create_work_order():
    title = request.form['title']
    description = request.form['description']
    created_by = request.form['created_by']
    new_order = WorkOrder(title=title, description=description, created_by=created_by)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('home'))

