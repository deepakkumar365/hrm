#!/usr/bin/env python3
"""
Script to fix role names to match application expectations
"""

from app import app, db
from models import Role

def fix_roles():
    with app.app_context():
        # Mapping of old names to new names
        role_updates = {
            'SUPER_ADMIN': 'Super Admin',
            'ADMIN': 'Admin',
            'HR_MANAGER': 'HR Manager',
            'EMPLOYEE': 'Employee'
        }

        for old_name, new_name in role_updates.items():
            role = Role.query.filter_by(name=old_name).first()
            if role:
                role.name = new_name
                print(f"Updated role {old_name} to {new_name}")
            else:
                print(f"Role {old_name} not found")

        db.session.commit()
        print("Role names updated")

if __name__ == '__main__':
    fix_roles()