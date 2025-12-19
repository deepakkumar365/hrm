import os
import uuid
from datetime import datetime
from sqlalchemy import text
from werkzeug.security import generate_password_hash
os.environ['ENVIRONMENT'] = 'development'
from app import app, db
from core.models import User, Role, Organization, Tenant, TenantConfiguration, Department, WorkingHours, WorkSchedule, Designation
from routes.routes_access_control import initialize_access_control_matrix

with app.app_context():
    try:
        print("1. Truncating...")
        hrm_tables = ["hrm_users", "hrm_roles", "organization", "role", "users"] # Minimal set for debug
        tables_str = ", ".join(hrm_tables)
        db.session.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;"))
        db.session.commit()
        db.session.expunge_all()
        print("Truncate Done.")

        print("2. Roles...")
        roles_data = [("Super Admin", "Desc"), ("Tenant Admin", "Desc")]
        roles_objs = {}
        for n, d in roles_data:
            r = Role(name=n, description=d)
            db.session.add(r)
            roles_objs[n] = r
        db.session.flush()
        print(f"Roles Done: {[r.id for r in roles_objs.values()]}")

        print("3. Tenant...")
        t = Tenant(id=uuid.uuid4(), name="Noltrion", code="NOL")
        db.session.add(t)
        db.session.flush()
        print(f"Tenant Done: {t.id}")

        print("4. Org...")
        o = Organization(name="Noltrion Org", tenant_id=t.id)
        db.session.add(o)
        db.session.flush()
        print(f"Org Done: {o.id}")

        print("5. User...")
        sql = text("""
        INSERT INTO hrm_users (username, email, password_hash, first_name, last_name, organization_id, role_id, is_active, must_reset_password)
        VALUES (:u, :e, :p, :f, :l, :o, :r, :a, :m)
        """)
        db.session.execute(sql, {
            'u': 'superadmin@noltrion.com',
            'e': 'superadmin@noltrion.com',
            'p': generate_password_hash('Admin@123'),
            'f': 'Super', 'l': 'Admin',
            'o': o.id, 'r': roles_objs["Super Admin"].id,
            'a': True, 'm': False
        })
        print("User Done.")

        print("6. Committing...")
        db.session.commit()
        print("Commit Successful.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
