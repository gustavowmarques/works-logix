# seed_roles.py

from app import create_app, db
from app.models import Role, BusinessType

def seed_data():
    app = create_app()
    with app.app_context():
        # Define default roles
        roles = [
            Role(name="Admin"),
            Role(name="Property Manager"),
            Role(name="Contractor"),
        ]

        # Define default business types
        business_types = [
            BusinessType(name="Plumbing"),
            BusinessType(name="Electrical"),
            BusinessType(name="Security"),
            BusinessType(name="Landscaping"),
            BusinessType(name="Cleaning"),
            BusinessType(name="Waste Collector"),
            BusinessType(name="Pest Control"),
        ]

        # Add only if table is empty
        if not Role.query.first():
            db.session.add_all(roles)
        if not BusinessType.query.first():
            db.session.add_all(business_types)

        db.session.commit()
        print("✅ Default roles and business types seeded successfully.")

if __name__ == "__main__":
    seed_data()
