from app import db
from app.models import Role, RolePermission

def seed_permissions():
    roles_permissions = {
        "Admin": [
            "view_admin_dashboard",
            "manage_users",
            "edit_clients",
            "view_reports",
            "manage_roles"
        ],
        "Property Manager": [
            "view_pm_dashboard",
            "edit_work_orders",
            "view_clients",
            "upload_documents",
            "view_reports"
        ],
        "Contractor": [
            "view_contractor_dashboard",
            "update_work_order_status",
            "upload_completion_media",
            "view_assigned_clients"
        ],
        "Director": [
            "view_director_dashboard",
            "view_capex_requests",
            "review_quotes",
            "submit_votes"
        ]
    }

    for role_name, permissions in roles_permissions.items():
        role = Role.query.filter(db.func.lower(Role.name) == role_name.lower()).first()
        if not role:
            print(f"Role '{role_name}' not found. Skipping.")
            continue

        for perm in permissions:
            exists = RolePermission.query.filter_by(role_id=role.id, permission=perm).first()
            if not exists:
                rp = RolePermission(role_id=role.id, permission=perm)
                db.session.add(rp)
                print(f"Added permission '{perm}' to role '{role_name}'")
            else:
                print(f"Permission '{perm}' already exists for role '{role_name}'")

    db.session.commit()
    print("Permission seeding complete.")
