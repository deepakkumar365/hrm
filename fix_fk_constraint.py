
import sys
import os
from sqlalchemy import text

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    from app import app, db
    print("Successfully imported app and db")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def fix_constraint():
    with app.app_context():
        try:
            print("Dropping legacy constraint 'hrm_users_role_id_fkey'...")
            db.session.execute(text("ALTER TABLE hrm_users DROP CONSTRAINT IF EXISTS hrm_users_role_id_fkey"))
            
            print("Adding correct constraint referencing 'hrm_roles'...")
            db.session.execute(text("ALTER TABLE hrm_users ADD CONSTRAINT hrm_users_role_id_fkey FOREIGN KEY (role_id) REFERENCES hrm_roles(id)"))
            
            db.session.commit()
            print("Successfully updated foreign key constraint.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating constraint: {e}")

if __name__ == "__main__":
    fix_constraint()
