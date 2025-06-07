from app.extensions import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# ----------------------------
# BUSINESS TYPES
# ----------------------------
class BusinessType(db.Model):
    __tablename__ = 'business_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# ----------------------------
# ROLES
# ----------------------------
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission = db.Column(db.String(100), nullable=False)

# ----------------------------
# USERS
# ----------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120))
    telephone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref='users', lazy=True)

    # Contractor-specific business type
    business_type_id = db.Column(db.Integer, db.ForeignKey('business_types.id'))
    business_type = db.relationship("BusinessType", foreign_keys=[business_type_id])

    # Company (e.g., Management Company they work for)
    company_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    company = db.relationship("Client", foreign_keys=[company_id], backref="employees")

    # Flask-Login integration
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


# ----------------------------
# CLIENT COMPANIES
# ----------------------------
class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(150), nullable=False)

    # Address fields
    street = db.Column(db.String(255))
    city = db.Column(db.String(100))
    county = db.Column(db.String(100))
    eircode = db.Column(db.String(20))
    country = db.Column(db.String(100))

    registration_number = db.Column(db.String(100))
    year_of_construction = db.Column(db.Integer)
    number_of_units = db.Column(db.Integer)

    # Foreign Key to assigned PM
    assigned_pm_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    assigned_pm = db.relationship("User", backref="assigned_clients", foreign_keys=[assigned_pm_id])

    users = db.relationship(
        "User",
        backref="client",
        foreign_keys="User.company_id"
    )

    work_orders = db.relationship(
        'WorkOrder',
        backref='client_data',
        lazy=True
    )

# ----------------------------
# CLIENTS AND CONTRACTOR M2M
# ----------------------------
class ClientContractor(db.Model):
    __tablename__ = 'client_contractor'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ----------------------------
# CONTRACTOR PERFORMANCE
# ----------------------------
class ContractorPerformance(db.Model):
    __tablename__ = 'contractor_performance'
    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    reaction_time_minutes = db.Column(db.Integer)
    completion_time_minutes = db.Column(db.Integer)
    performance_rating = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------------------
# MEDIA FILES
# ----------------------------
class MediaFile(db.Model):
    __tablename__ = 'media_files'
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------------------
# EXISTING TABLES (SAMPLE: WORK ORDER)
# ----------------------------
class WorkOrder(db.Model):
    __tablename__ = 'work_order'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    status = db.Column(db.String(50))
    created_by = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    preferred_contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    second_preferred_contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    business_type = db.Column(db.String(100))
    rejected_by = db.Column(db.String(120))
    completion_photo = db.Column(db.String(255))
    occupant_name = db.Column(db.String(120))
    occupant_apartment = db.Column(db.String(50))
    occupant_phone = db.Column(db.String(50))
    due_date = db.Column(db.Date)

