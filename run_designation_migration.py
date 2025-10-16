#!/usr/bin/env python3
"""
Designation and Role Enhancement Migration Script
This script:
1. Creates hrm_designations table
2. Creates hrm_employee_companies association table
3. Creates hrm_user_roles association table
4. Adds designation_id to hrm_employees
5. Migrates existing position data to designations
"""

import psycopg2
from psycopg2 import sql
import sys

# Database connection details from .env
DB_CONFIG = {
    'dbname': 'pgnoltrion',
    'user': 'noltrion_admin',
    'password': 'xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y',
    'host': 'dpg-d2kq4515pdvs739uk9h0-a.oregon-postgres.render.com',
    'port': '5432'
}

def execute_sql(cursor, sql_statement, description):
    """Execute SQL and print status"""
    try:
        print(f"\n{'='*60}")
        print(f"⚙️  {description}")
        print(f"{'='*60}")
        cursor.execute(sql_statement)
        print(f"✅ SUCCESS: {description}")
        return True
    except Exception as e:
        print(f"❌ ERROR: {description}")
        print(f"   {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 STARTING DESIGNATION & ROLE ENHANCEMENT MIGRATION")
    print("="*60)
    
    conn = None
    try:
        # Connect to database
        print("\n📡 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        
        # Step 1: Create hrm_designations table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS hrm_designations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, "Creating hrm_designations table")
        
        # Step 2: Create indexes for hrm_designations
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_designations_name ON hrm_designations(name)
        """, "Creating index on hrm_designations.name")
        
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_designations_is_active ON hrm_designations(is_active)
        """, "Creating index on hrm_designations.is_active")
        
        # Step 3: Migrate existing position data to designations
        print("\n" + "="*60)
        print("📊 MIGRATING POSITION DATA")
        print("="*60)
        
        cursor.execute("""
            SELECT DISTINCT position 
            FROM hrm_employees 
            WHERE position IS NOT NULL AND position != ''
            ORDER BY position
        """)
        positions = cursor.fetchall()
        
        if positions:
            print(f"📋 Found {len(positions)} unique positions to migrate")
            for position in positions:
                position_name = position[0]
                try:
                    cursor.execute("""
                        INSERT INTO hrm_designations (name, description, is_active)
                        VALUES (%s, %s, TRUE)
                        ON CONFLICT (name) DO NOTHING
                    """, (position_name, f"Migrated from position field"))
                    print(f"   ✅ Migrated: {position_name}")
                except Exception as e:
                    print(f"   ⚠️  Skipped {position_name}: {str(e)}")
        else:
            print("📋 No positions found to migrate")
        
        # Step 4: Add designation_id column to hrm_employees
        execute_sql(cursor, """
            ALTER TABLE hrm_employees
            ADD COLUMN IF NOT EXISTS designation_id INTEGER
        """, "Adding designation_id column to hrm_employees")
        
        # Step 5: Create foreign key for designation_id
        execute_sql(cursor, """
            ALTER TABLE hrm_employees
            DROP CONSTRAINT IF EXISTS hrm_employees_designation_id_fkey
        """, "Dropping old designation_id foreign key if exists")
        
        execute_sql(cursor, """
            ALTER TABLE hrm_employees
            ADD CONSTRAINT hrm_employees_designation_id_fkey
            FOREIGN KEY (designation_id) REFERENCES hrm_designations(id)
        """, "Creating foreign key for designation_id")
        
        # Step 6: Update designation_id based on position
        print("\n" + "="*60)
        print("🔄 UPDATING EMPLOYEE DESIGNATION IDs")
        print("="*60)
        
        cursor.execute("""
            UPDATE hrm_employees e
            SET designation_id = d.id
            FROM hrm_designations d
            WHERE e.position = d.name
            AND e.designation_id IS NULL
        """)
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} employee records with designation_id")
        
        # Step 7: Create hrm_employee_companies association table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS hrm_employee_companies (
                employee_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (employee_id, company_id),
                FOREIGN KEY (employee_id) REFERENCES hrm_employees(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES hrm_companies(id) ON DELETE CASCADE
            )
        """, "Creating hrm_employee_companies association table")
        
        # Step 8: Create indexes for hrm_employee_companies
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_employee_companies_employee 
            ON hrm_employee_companies(employee_id)
        """, "Creating index on hrm_employee_companies.employee_id")
        
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_employee_companies_company 
            ON hrm_employee_companies(company_id)
        """, "Creating index on hrm_employee_companies.company_id")
        
        # Step 9: Migrate existing company_id to hrm_employee_companies
        print("\n" + "="*60)
        print("🔄 MIGRATING EMPLOYEE-COMPANY RELATIONSHIPS")
        print("="*60)
        
        cursor.execute("""
            INSERT INTO hrm_employee_companies (employee_id, company_id)
            SELECT id, company_id
            FROM hrm_employees
            WHERE company_id IS NOT NULL
            ON CONFLICT (employee_id, company_id) DO NOTHING
        """)
        migrated_count = cursor.rowcount
        print(f"✅ Migrated {migrated_count} employee-company relationships")
        
        # Step 10: Create hrm_user_roles association table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS hrm_user_roles (
                user_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES hrm_roles(id) ON DELETE CASCADE
            )
        """, "Creating hrm_user_roles association table")
        
        # Step 11: Create indexes for hrm_user_roles
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_user_roles_user 
            ON hrm_user_roles(user_id)
        """, "Creating index on hrm_user_roles.user_id")
        
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_user_roles_role 
            ON hrm_user_roles(role_id)
        """, "Creating index on hrm_user_roles.role_id")
        
        # Step 12: Migrate existing role_id to hrm_user_roles
        print("\n" + "="*60)
        print("🔄 MIGRATING USER-ROLE RELATIONSHIPS")
        print("="*60)
        
        cursor.execute("""
            INSERT INTO hrm_user_roles (user_id, role_id)
            SELECT id, role_id
            FROM hrm_users
            WHERE role_id IS NOT NULL
            ON CONFLICT (user_id, role_id) DO NOTHING
        """)
        migrated_roles_count = cursor.rowcount
        print(f"✅ Migrated {migrated_roles_count} user-role relationships")
        
        # Commit all changes
        conn.commit()
        print("\n" + "="*60)
        print("✅ TRANSACTION COMMITTED")
        print("="*60)
        
        # Step 13: Verification
        print("\n" + "="*60)
        print("🔍 VERIFICATION")
        print("="*60)
        
        # Check hrm_designations
        cursor.execute("SELECT COUNT(*) FROM hrm_designations")
        designation_count = cursor.fetchone()[0]
        print(f"\n✅ hrm_designations table has {designation_count} records")
        
        # Show sample designations
        cursor.execute("SELECT id, name, is_active FROM hrm_designations ORDER BY name LIMIT 5")
        designations = cursor.fetchall()
        print("\n📋 Sample designations:")
        for designation in designations:
            print(f"   ID: {designation[0]}, Name: {designation[1]}, Active: {designation[2]}")
        
        # Check hrm_employee_companies
        cursor.execute("SELECT COUNT(*) FROM hrm_employee_companies")
        emp_company_count = cursor.fetchone()[0]
        print(f"\n✅ hrm_employee_companies table has {emp_company_count} records")
        
        # Check hrm_user_roles
        cursor.execute("SELECT COUNT(*) FROM hrm_user_roles")
        user_role_count = cursor.fetchone()[0]
        print(f"\n✅ hrm_user_roles table has {user_role_count} records")
        
        # Check employees with designation_id
        cursor.execute("""
            SELECT COUNT(*) FROM hrm_employees WHERE designation_id IS NOT NULL
        """)
        emp_with_designation = cursor.fetchone()[0]
        print(f"\n✅ {emp_with_designation} employees have designation_id assigned")
        
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. Test Designation Master CRUD operations")
        print("   3. Test employee form with designation dropdown")
        print("   4. Test multiple company assignment")
        print("   5. Test multiple role assignment")
        print("   6. Verify role-based access controls")
        
        cursor.close()
        return 0
        
    except psycopg2.Error as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        if conn:
            conn.rollback()
            print("🔄 Transaction rolled back")
        return 1
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        if conn:
            conn.rollback()
            print("🔄 Transaction rolled back")
        return 1
        
    finally:
        if conn:
            conn.close()
            print("\n📡 Database connection closed")

if __name__ == "__main__":
    sys.exit(main())