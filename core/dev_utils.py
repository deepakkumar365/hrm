"""
Utility functions for development-only tasks.
"""
import os
import uuid
from datetime import datetime
from flask import current_app
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from app import db
from core.models import User, Role, Organization, Tenant, TenantConfiguration, Department, WorkingHours, WorkSchedule, Designation
from routes.routes_access_control import initialize_access_control_matrix

def clean_database_hrm():
    """
    Cleans all HRM and core tables and re-seeds default data.
    STRICTLY FOR DEVELOPMENT MODE.
    """
    if os.environ.get('ENVIRONMENT') != 'development':
        return False, "Database cleanup is only allowed in development mode."

    try:
        # 1. Targeted HRM and Core Tables
        hrm_tables = [
            "hrm_appraisal", "hrm_attendance", "hrm_audit_log", "hrm_claim", 
            "hrm_company_employee_id_config", "hrm_compliance_report", 
            "hrm_designation_leave_allocation", "hrm_employee_bank_info", 
            "hrm_employee_documents", "hrm_employee_group_leave_allocation", 
            "hrm_employee_leave_allocation", "hrm_leave", "hrm_ot_approval", 
            "hrm_ot_attendance", "hrm_ot_daily_summary", "hrm_ot_request", 
            "hrm_ot_type", "hrm_payroll", "hrm_payroll_configuration", 
            "hrm_payroll_ot_summary", "hrm_tenant_documents", 
            "hrm_tenant_payment_config", "hrm_user_company_access", 
            "hrm_user_role_mapping", "hrm_employee", "hrm_leave_type", 
            "hrm_employee_group", "hrm_departments", "hrm_designation", 
            "hrm_work_schedules", "hrm_working_hours", "hrm_company", 
            "hrm_tenant_configuration", "hrm_tenant", "hrm_users", 
            "hrm_roles", "organization", "role", "users"
        ]

        # Use a single large truncate command to handle dependencies efficiently
        tables_str = ", ".join(hrm_tables)
        try:
            db.session.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;"))
            db.session.commit()
            db.session.expunge_all() # Clear all stale objects from session
            print("All tables truncated and session cleared successfully.")
        except Exception as te:
            db.session.rollback()
            db.session.expunge_all()
            print(f"TRUNCATE failed: {te}. Falling back to individual deletes...")
            for table in hrm_tables:
                try:
                    db.session.execute(text(f"DELETE FROM {table}"))
                except Exception as de:
                    print(f"Could not delete from {table}: {de}")
            db.session.commit()
            db.session.expunge_all()

        # 2. Re-seed essential data
        print("Re-seeding essential data...")
        
        # 2.1 Roles (Matching ROLE_NAMES in routes_access_control.py)
        # We seed BOTH 'role' and 'hrm_roles' because hrm_users.role_id 
        # points to 'role' in the database but Role model maps to 'hrm_roles'.
        roles_data = [
            ("Super Admin", "Super administrator with all permissions."),
            ("Tenant Admin", "Administrator with organization-wide permissions."),
            ("HR Manager", "HR manager with employee management permissions."),
            ("Employee", "Regular employee with limited permissions."),
        ]
        roles_objs = {}
        for r_name, r_desc in roles_data:
            # Seed hrm_roles (SQLAlchemy Model)
            role = Role(name=r_name, description=r_desc)
            db.session.add(role)
            db.session.flush()
            roles_objs[r_name] = role
            
            # Seed role (Lowercase table for DB constraint)
            db.session.execute(text("INSERT INTO role (id, name, description) VALUES (:id, :name, :description)"), 
                               {"id": role.id, "name": r_name, "description": r_desc})
        
        db.session.flush()

        # 2.2 Tenant (Default)
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Noltrion",
            code="NOL",
            is_active=True,
            created_by="system"
        )
        db.session.add(tenant)
        db.session.flush()

        # 2.3 Organization
        org = Organization(
            name="Noltrion Invovation Pvt Ltd",
            tenant_id=tenant.id,
            created_by="system"
        )
        db.session.add(org)
        db.session.flush()

        # 2.4 User (Superadmin)
        print("Creating superadmin user...")
        # Using raw SQL to be absolutely certain about the insert
        sql = text("""
        INSERT INTO hrm_users (username, email, password_hash, first_name, last_name, organization_id, role_id, is_active, must_reset_password)
        VALUES (:u, :e, :p, :f, :l, :o, :r, :a, :m)
        """)
        
        db.session.execute(sql, {
            'u': 'superadmin@noltrion.com',
            'e': 'superadmin@noltrion.com',
            'p': generate_password_hash('Admin@123'),
            'f': 'Super',
            'l': 'Admin',
            'o': org.id,
            'r': roles_objs["Super Admin"].id,
            'a': True,
            'm': False
        })

        # 2.5 Tenant Configuration
        tenant_config = TenantConfiguration(
            tenant_id=tenant.id,
            employee_id_prefix="NOL",
            employee_id_format="prefix-number",
            employee_id_next_number=1,
            created_at=datetime.now()
        )
        db.session.add(tenant_config)

        # 2.6 Basic Master Data
        depts = ["IT", "HR", "Finance", "Sales", "Operations"]
        for d_name in depts:
            db.session.add(Department(name=d_name, is_active=True))

        designations = ["Software Engineer", "HR Manager", "Accountant", "Sales Executive", "Operations Manager"]
        for ds_name in designations:
            db.session.add(Designation(name=ds_name, is_active=True))

        standard_wh = WorkingHours(name="Standard", hours_per_day=8, hours_per_week=40, is_active=True)
        db.session.add(standard_wh)

        from datetime import time
        standard_ws = WorkSchedule(name="9-6 Shift", start_time=time(9, 0), end_time=time(18, 0), is_active=True)
        db.session.add(standard_ws)

        # 2.7 RBAC
        # This function re-initializes permissions for the roles we just created
        initialize_access_control_matrix()

        db.session.commit()
        return True, "Database cleaned and re-seeded successfully."

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return False, f"Cleanup failed: {str(e)}"
