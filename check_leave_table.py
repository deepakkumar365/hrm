"""Check if hrm_leave_type table exists in the database"""
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n=== Database Table Check ===")
    print(f"Total tables: {len(tables)}")
    print(f"\nhrm_leave_type exists: {'hrm_leave_type' in tables}")
    
    if 'hrm_leave_type' in tables:
        print("\n✓ hrm_leave_type table exists")
        columns = inspector.get_columns('hrm_leave_type')
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("\n✗ hrm_leave_type table does NOT exist")
        print("\nYou need to run migrations:")
        print("  flask db upgrade")
    
    print("\n=== All Tables ===")
    for table in sorted(tables):
        print(f"  - {table}")