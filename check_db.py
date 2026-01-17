
import os
from app import app, db
from sqlalchemy import inspect

def check_tables():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {len(tables)}")
        if 'hrm_file_storage' in tables:
            print("[OK] hrm_file_storage exists.")
            # Check columns
            cols = [c['name'] for c in inspector.get_columns('hrm_file_storage')]
            print(f"Columns: {cols}")
        else:
            print("[FAIL] hrm_file_storage MISSING.")

if __name__ == "__main__":
    check_tables()
