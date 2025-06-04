from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.decorators import permission_required
from app.models import User, Role, WorkOrder, Client, db, BusinessType
from werkzeug.security import generate_password_hash




admin_routes_bp = Blueprint('admin_routes', __name__)


@admin_routes_bp.route('/admin/dashboard') 
@login_required
@permission_required("view_admin_dashboard")
def admin_dashboard():
    return render_template("admin/admin_dashboard.html")

# View All Work Orders
@admin_routes_bp.route('/admin/work-orders', endpoint='admin_work_orders')
@login_required
def admin_work_orders():
    work_orders = WorkOrder.query.all() 
    return render_template("admin/admin_work_orders.html", work_orders=work_orders)


# View All Users
@admin_routes_bp.route('/admin/users')
@login_required
@permission_required("view_admin_dashboard")
def view_all_users():
    users = User.query.all()
    return render_template('admin/view_all_users.html', users=users)

# View All Clients
@admin_routes_bp.route('/admin/clients', endpoint='view_all_clients')
@login_required
@permission_required("view_admin_dashboard")
def view_all_clients():
    clients = Client.query.all()
    return render_template('admin/view_all_clients.html', clients=clients)


@admin_routes_bp.route('/admin/clients/register', methods=['GET', 'POST'], endpoint='register_client')
@login_required
@permission_required("view_admin_dashboard")
def register_client():

    if request.method == 'POST':
        name = request.form.get('name')
        street = request.form.get('street')
        city = request.form.get('city')
        county = request.form.get('county')
        eircode = request.form.get('eircode')
        country = request.form.get('country')
        registration_number = request.form.get('registration_number')
        year_of_construction = request.form.get('year_of_construction')
        number_of_units = request.form.get('number_of_units')
        property_manager_id = request.form.get('property_manager_id')

        if not name or not street or not city or not county or not country:
            flash("All address fields and name are required.", "danger")
            return redirect(url_for('admin_routes.register_client'))

        new_client = Client(
            name=name,
            street=street,
            city=city,
            county=county,
            eircode=eircode,
            country=country,
            registration_number=registration_number,
            year_of_construction=year_of_construction,
            number_of_units=number_of_units,
            assigned_pm_id=property_manager_id if property_manager_id else None
        )


        if property_manager_id:
            assigned_manager = User.query.get(property_manager_id)
            if assigned_manager:
                assigned_manager.company_id = new_client.id  # Will be set after commit

        db.session.add(new_client)
        db.session.commit()

        # After committing, assign the company_id
        if property_manager_id and assigned_manager:
            assigned_manager.company_id = new_client.id
            db.session.commit()

        flash("Client registered successfully.", "success")
        return redirect(url_for('admin_routes.view_all_clients'))

    # For GET requests, load all Property Managers
    property_managers = User.query.join(Role).filter(Role.name == 'Property Manager').all()

    return render_template('admin/register_client.html', property_managers=property_managers)


# View All Contractors
@admin_routes_bp.route('/admin/contractors', endpoint='view_all_contractors')
@login_required
@permission_required("view_all_contractors")
def view_all_contractors():
    from app.models import User, Role
    contractors = User.query.join(Role).filter(Role.name.ilike('Contractor')).all()
    return render_template('admin/view_all_contractors.html', contractors=contractors)


@admin_routes_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'], endpoint='edit_user')
@login_required
@permission_required("edit_user")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()

    if request.method == "POST":
        user.email = request.form.get("email")
        user.role_id = request.form.get("role_id")
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_routes.view_all_users'))

    return render_template('admin/edit_user.html', user=user, roles=roles)

@admin_routes_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'], endpoint='delete_user')
@login_required
@permission_required("delete_user")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_routes.view_all_users'))

@admin_routes_bp.route('/admin/users/register', methods=['GET', 'POST'], endpoint='register_user')
@login_required
@permission_required('admin')
def register_user():
    roles = Role.query.all()
    companies = Client.query.all()
    clients = Client.query.all()
    business_types = BusinessType.query.all()

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        company_id = request.form.get('company_id')
        client_id = request.form.get('client_id') or None
        business_type_id = request.form.get('business_type_id') or None

        hashed_password = generate_password_hash(password)
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            role_id=role_id,
            company_id=company_id,
            client_id=client_id,
            business_type_id=business_type_id
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully.', 'success')
        return redirect(url_for('admin_routes.view_all_users'))

    return render_template('admin/register_user.html', roles=roles, companies=companies, clients=clients, business_types=business_types)

