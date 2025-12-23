
import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    from app import app, db
    print("Successfully imported app and db")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

from sqlalchemy import text

with app.app_context():
    print("--- Checking 'hrm_roles' table (via SQLAlchemy model) ---")
    try:
        from core.models import Role
        roles = Role.query.all()
        for r in roles:
            print(f"ID: {r.id}, Name: {r.name}")
    except Exception as e:
        print(f"Error querying Role model: {e}")

    print("\n--- Checking 'role' table (via raw SQL) ---")
    try:
        result = db.session.execute(text("SELECT id, name FROM role"))
        rows = list(result)
        if not rows:
            print("Table 'role' is empty.")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}")
    except Exception as e:
        print(f"Error querying 'role' table: {e}")

    print("\n--- Checking Foreign Key Constraints on 'hrm_users' ---")
    try:
        sql = """
        SELECT
            tc.constraint_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='hrm_users';
        """
        result = db.session.execute(text(sql))
        for row in result:
            print(f"Constraint: {row[0]}, Column: {row[1]}, Ref Table: {row[2]}, Ref Column: {row[3]}")
    except Exception as e:
        print(f"Error checking constraints: {e}")
