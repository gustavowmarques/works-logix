from app import create_app, db
from app.models import Role, RolePermission

app = create_app()

# Define permissions for each role
permissions_by_role = {
    'Admin': [
        'create_user', 'edit_user', 'delete_user',
        'create_client', 'edit_client', 'delete_client',
        'create_work_order', 'edit_work_order', 'delete_work_order',
        'assign_contractor', 'view_all_reports'
    ],
    'Property Manager': [
        'create_work_order', 'edit_own_work_order', 'delete_own_work_order',
        'reassign_work_order', 'view_assigned_reports'
    ],
    'Contractor': [
        'view_assigned_work_order', 'complete_work_order', 'upload_files'
    ]
}

with app.app_context():
    for role_name, actions in permissions_by_role.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            print(f"❌ Role not found: {role_name}")
            continue

        for action in actions:
            exists = RolePermission.query.filter_by(role_id=role.id, permission=action).first()
            if not exists:
                db.session.add(RolePermission(role_id=role.id, permission=action))
                print(f"✅ Added permission '{action}' to role '{role_name}'")

    db.session.commit()
    print("🎉 Role permissions seeded successfully.")
