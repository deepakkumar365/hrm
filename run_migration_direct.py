#!/usr/bin/env python3
"""
Direct Migration Script - No User Input Required
Connects directly to database and runs the migration
"""

import psycopg2
from psycopg2 import sql
import sys

# Database connection details from .env
DB_CONFIG = {
    'dbname': 'pgnoltrion',
    'user': 'noltrion_admin',
    'password': 'xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y',
    'host': 'dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com',
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
    print("🚀 STARTING ROLE TABLE MIGRATION")
    print("="*60)
    
    conn = None
    try:
        # Connect to database
        print("\n📡 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        
        # Step 1: Check current state
        print("\n" + "="*60)
        print("📊 CHECKING CURRENT STATE")
        print("="*60)
        
        cursor.execute("SELECT COUNT(*) FROM role")
        role_count = cursor.fetchone()[0]
        print(f"📋 Old 'role' table has {role_count} records")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'hrm_roles'
        """)
        hrm_roles_exists = cursor.fetchone()[0] > 0
        
        if hrm_roles_exists:
            cursor.execute("SELECT COUNT(*) FROM hrm_roles")
            hrm_roles_count = cursor.fetchone()[0]
            print(f"📋 New 'hrm_roles' table has {hrm_roles_count} records")
        else:
            print("📋 New 'hrm_roles' table does not exist yet")
        
        # Step 2: Create hrm_roles table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS hrm_roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(80) UNIQUE NOT NULL,
                description VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, "Creating hrm_roles table")
        
        # Step 3: Copy data if hrm_roles is empty
        cursor.execute("SELECT COUNT(*) FROM hrm_roles")
        if cursor.fetchone()[0] == 0:
            execute_sql(cursor, """
                INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
                SELECT id, name, description, is_active, created_at, updated_at
                FROM role
                ORDER BY id
            """, "Copying data from role to hrm_roles")
            
            # Update sequence
            execute_sql(cursor, """
                SELECT setval('hrm_roles_id_seq', (SELECT MAX(id) FROM hrm_roles))
            """, "Updating sequence")
        else:
            print("\n✅ hrm_roles already has data, skipping copy")
        
        # Step 4: Find and drop ALL foreign key constraints on hrm_users.role_id
        print("\n" + "="*60)
        print("🔍 FINDING FOREIGN KEY CONSTRAINTS")
        print("="*60)
        
        cursor.execute("""
            SELECT tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'hrm_users' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'role_id'
        """)
        
        constraints = cursor.fetchall()
        if constraints:
            print(f"📋 Found {len(constraints)} constraint(s) to drop:")
            for constraint in constraints:
                constraint_name = constraint[0]
                print(f"   - {constraint_name}")
                execute_sql(cursor, 
                    f"ALTER TABLE hrm_users DROP CONSTRAINT IF EXISTS {constraint_name}",
                    f"Dropping constraint: {constraint_name}")
        else:
            print("✅ No foreign key constraints found (already dropped)")
        
        # Step 5: Create NEW foreign key pointing to hrm_roles
        execute_sql(cursor, """
            ALTER TABLE hrm_users
            ADD CONSTRAINT hrm_users_role_id_fkey
            FOREIGN KEY (role_id) REFERENCES hrm_roles(id)
        """, "Creating new foreign key to hrm_roles")
        
        # Step 6: Create indexes
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_roles_name ON hrm_roles(name)
        """, "Creating index on hrm_roles.name")
        
        execute_sql(cursor, """
            CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active ON hrm_roles(is_active)
        """, "Creating index on hrm_roles.is_active")
        
        # Step 7: Drop old role table
        execute_sql(cursor, """
            DROP TABLE IF EXISTS role CASCADE
        """, "Dropping old 'role' table")
        
        # Commit all changes
        conn.commit()
        print("\n" + "="*60)
        print("✅ TRANSACTION COMMITTED")
        print("="*60)
        
        # Step 8: Verification
        print("\n" + "="*60)
        print("🔍 VERIFICATION")
        print("="*60)
        
        # Check hrm_roles data
        cursor.execute("SELECT COUNT(*) FROM hrm_roles")
        final_count = cursor.fetchone()[0]
        print(f"\n✅ hrm_roles table has {final_count} records")
        
        # Show sample data
        cursor.execute("SELECT id, name, is_active FROM hrm_roles ORDER BY id LIMIT 5")
        roles = cursor.fetchall()
        print("\n📋 Sample roles:")
        for role in roles:
            print(f"   ID: {role[0]}, Name: {role[1]}, Active: {role[2]}")
        
        # Check foreign key
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'hrm_users' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'role_id'
        """)
        
        fk_info = cursor.fetchone()
        if fk_info:
            print(f"\n✅ Foreign key verified:")
            print(f"   Constraint: {fk_info[0]}")
            print(f"   Column: {fk_info[1]}")
            print(f"   References: {fk_info[2]}.{fk_info[3]}")
        
        # Check old table is gone
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'role'
        """)
        old_table_exists = cursor.fetchone()[0] > 0
        
        if not old_table_exists:
            print("\n✅ Old 'role' table successfully removed")
        else:
            print("\n⚠️  WARNING: Old 'role' table still exists!")
        
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. Test user login functionality")
        print("   3. Verify role-based access control")
        print("   4. Check admin panel for role management")
        
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