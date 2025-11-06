"""
Seed roles, default organization, and update existing users for HRMS hierarchy.
Run this script after applying the HRMS migration.
"""
from app import db, app
from models import Role, Organization, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Seed roles
    roles = [
        {"name": "Super Admin", "description": "Product admin; can create organizations and Admin users."},
        {"name": "Admin", "description": "Organization admin; manages HR Managers and employees."},
        {"name": "HR Manager", "description": "Manages employees of the organization."},
        {"name": "Employee", "description": "Standard employee."},
    ]
    for role_data in roles:
        role = Role.query.filter_by(name=role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
    db.session.commit()

    # 2. Seed default organization
    org = Organization.query.filter_by(name="Nexar HQ").first()
    if not org:
        org = Organization(name="Nexar HQ")
        db.session.add(org)
        db.session.commit()

    # 3. Map existing users
    super_admin_role = Role.query.filter_by(name="Super Admin").first()
    admin_role = Role.query.filter_by(name="Admin").first()

    for user in User.query.all():
        # Assign Super Admin to first user, rest as Admins (customize as needed)
        if not user.role_id:
            if user.id == 1:
                user.role_id = super_admin_role.id
                user.organization_id = None
            else:
                user.role_id = admin_role.id
                user.organization_id = org.id
            user.must_reset_password = True
            # Set a secure default password if not set
            if not user.password_hash:
                user.password_hash = generate_password_hash("ChangeMe123!")
    db.session.commit()

    print("Seeded roles, organization, and updated users.")
