
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    required = ['hrm_employee', 'hrm_users', 'hrm_company']
    missing = [t for t in required if t not in tables]
    print(f"Tables found: {len(tables)}")
    if missing:
        print(f"MISSING TABLES: {missing}")
    else:
        print("Required tables present.")
