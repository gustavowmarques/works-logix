from .roles import UserRole
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from app.extensions import db


class WorkOrderStatus(Enum):
    OPEN = "Open"
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"
    
class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open')  
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    contractor = db.relationship("User", backref="accepted_work_orders")
    business_type = db.Column(db.String(100))  # Type of contractor service required

    completion_photo = db.Column(db.String(200), nullable=True)
    occupant_apartment = db.Column(db.String(120))
    occupant_phone = db.Column(db.String(120))
    occupant_name = db.Column(db.String(120))


    # New preferred contractor logic
    business_type = db.Column(db.String(100))  # Type of contractor service required
    preferred_contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    rejected_by = db.Column(db.String(500))  # Comma-separated contractor IDs who have rejected
 
    #backrefs for relationships
    client = db.relationship('Client', backref='work_orders')
    contractor = db.relationship('User', foreign_keys=[contractor_id])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(SQLAlchemyEnum(UserRole), nullable=False)
    business_type = db.Column(db.String(100), nullable=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    registration_number = db.Column(db.String(50), nullable=False)
    year_built = db.Column(db.Integer, nullable=False)
    number_of_units = db.Column(db.Integer, nullable=False)


class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_registration_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    accounts_contact_name = db.Column(db.String(100), nullable=False)
    accounts_contact_email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    business_type = db.Column(
        db.String(50),
        nullable=False
    )  # plumbing, electrical, security, etc.

rejected_by = db.Column(db.Integer, nullable=True)  # contractor_id who rejected it
