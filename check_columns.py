
from app import app, db
from sqlalchemy import inspect
from sqlalchemy import text

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('hrm_work_schedules')
    print("--- COLUMNS IN hrm_work_schedules ---")
    for col in columns:
        print(f"Column: {col['name']} ({col['type']})")
    print("--- END ---")
