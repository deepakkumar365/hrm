"""Quick role table analysis - Run this directly in PyCharm terminal"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def main():
    with app.app_context():
        print("=" * 80)
        print("ROLE TABLES ANALYSIS")
        print("=" * 80)
        
        # Check table existence
        print("\n1. Checking table existence...")
        result = db.session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('roles', 'hrm_roles')
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"   Found tables: {tables}")
        
        # Count rows
        print("\n2. Row counts...")
        if 'roles' in tables:
            result = db.session.execute(text("SELECT COUNT(*) FROM public.roles"))
            roles_count = result.scalar()
            print(f"   public.roles: {roles_count} rows")
        else:
            print("   public.roles: TABLE DOES NOT EXIST")
            roles_count = 0
            
        if 'hrm_roles' in tables:
            result = db.session.execute(text("SELECT COUNT(*) FROM public.hrm_roles"))
            hrm_roles_count = result.scalar()
            print(f"   public.hrm_roles: {hrm_roles_count} rows")
        else:
            print("   public.hrm_roles: TABLE DOES NOT EXIST")
            hrm_roles_count = 0
        
        # Show data from roles table
        if 'roles' in tables and roles_count > 0:
            print("\n3. Data in public.roles:")
            result = db.session.execute(text("SELECT * FROM public.roles ORDER BY id"))
            for row in result:
                print(f"   ID: {row[0]}, Name: {row[1] if len(row) > 1 else 'N/A'}")
        
        # Show data from hrm_roles table
        if 'hrm_roles' in tables and hrm_roles_count > 0:
            print("\n4. Data in public.hrm_roles:")
            result = db.session.execute(text("SELECT * FROM public.hrm_roles ORDER BY id"))
            for row in result:
                print(f"   ID: {row[0]}, Name: {row[1] if len(row) > 1 else 'N/A'}")
        
        # Check user role references
        print("\n5. Role IDs used by users:")
        result = db.session.execute(text("SELECT DISTINCT role_id FROM hrm_users ORDER BY role_id"))
        user_role_ids = [row[0] for row in result]
        print(f"   User role_ids: {user_role_ids}")
        
        # Check foreign key constraint
        print("\n6. Foreign key constraint on hrm_users.role_id:")
        result = db.session.execute(text("""
            SELECT
                tc.constraint_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'hrm_users'
            AND kcu.column_name = 'role_id'
        """))
        fk_info = result.fetchone()
        if fk_info:
            print(f"   Constraint: {fk_info[0]}")
            print(f"   References: {fk_info[1]}.{fk_info[2]}")
        else:
            print("   No foreign key constraint found!")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

if __name__ == '__main__':
    main()