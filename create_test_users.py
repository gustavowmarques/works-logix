from app import db, create_app
from app.models import User, Role, Client, BusinessType
from werkzeug.security import generate_password_hash
from datetime import datetime

# Setup Flask app context
app = create_app()
with app.app_context():
    # Lookup roles
    admin_role = Role.query.filter_by(name='Admin').first()
    pm_role = Role.query.filter_by(name='Property Manager').first()
    contractor_role = Role.query.filter_by(name='Contractor').first()

    # Lookup sample client/company and business type
    sample_client = Client.query.first()
    sample_business_type = BusinessType.query.first()

    # Create Admin user
    admin_user = User(
        email='admin@example.com',
        password_hash=generate_password_hash('Admin123!'),
        full_name='Admin User',
        role_id=admin_role.id,
        created_at=datetime.utcnow()
    )

    # Create Property Manager user
    pm_user = User(
        email='pm@example.com',
        password_hash=generate_password_hash('Pm123!'),
        full_name='Property Manager User',
        role_id=pm_role.id,
        company_id=sample_client.id,
        created_at=datetime.utcnow()
    )

    # Create Contractor user
    contractor_user = User(
        email='contractor@example.com',
        password_hash=generate_password_hash('Contractor123!'),
        full_name='Contractor User',
        role_id=contractor_role.id,
        company_id=sample_client.id,
        business_type_id=sample_business_type.id,
        created_at=datetime.utcnow()
    )

    # Add to session and commit
    db.session.add_all([admin_user, pm_user, contractor_user])
    db.session.commit()

    print("✅ Test users created successfully.")
