#!/usr/bin/env python3
"""
Script to fix company assignment for existing employees
"""

from app import app, db
from models import Employee, Company, Organization

def fix_companies():
    with app.app_context():
        # Check if there's a company
        company = Company.query.first()
        if not company:
            # Create default organization if needed
            org = Organization.query.first()
            if not org:
                org = Organization(name='Default Organization')
                db.session.add(org)
                db.session.flush()
            company = Company(name='Default Company', organization_id=org.id)
            db.session.add(company)
            db.session.flush()

        # Assign company to employees without company
        employees_without_company = Employee.query.filter_by(company_id=None).all()
        for emp in employees_without_company:
            emp.company_id = company.id
            print(f"Assigned company to {emp.employee_id} - {emp.first_name} {emp.last_name}")

        db.session.commit()
        print(f"Fixed {len(employees_without_company)} employees")

if __name__ == '__main__':
    fix_companies()