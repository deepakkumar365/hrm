"""
Script to analyze both public.roles and public.hrm_roles tables
and understand the data structure before migration
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'dpg-d2kq4515pdvs739uk9h0-a.oregon-postgres.render.com'),
    'database': os.getenv('DB_NAME', 'pgnoltrion'),
    'user': os.getenv('DB_USER', 'noltrion_admin'),
    'password': os.getenv('DB_PASSWORD', 'Ry0Ks0Ks0Ks0Ks0Ks0Ks0Ks0Ks0Ks0'),
    'port': os.getenv('DB_PORT', '5432')
}

def analyze_tables():
    """Analyze both roles tables"""
    conn = None
    try:
        print("=" * 80)
        print("ANALYZING ROLES TABLES")
        print("=" * 80)
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if public.roles table exists
        print("\n1. Checking if public.roles table exists...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'roles'
            );
        """)
        roles_exists = cursor.fetchone()['exists']
        print(f"   public.roles exists: {roles_exists}")
        
        # Check if public.hrm_roles table exists
        print("\n2. Checking if public.hrm_roles table exists...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_roles'
            );
        """)
        hrm_roles_exists = cursor.fetchone()['exists']
        print(f"   public.hrm_roles exists: {hrm_roles_exists}")
        
        # Analyze public.roles if it exists
        if roles_exists:
            print("\n" + "=" * 80)
            print("ANALYZING public.roles TABLE")
            print("=" * 80)
            
            # Get table structure
            print("\n3. Structure of public.roles:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'roles'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} "
                      f"(nullable: {col['is_nullable']}, default: {col['column_default']})")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) as count FROM public.roles;")
            count = cursor.fetchone()['count']
            print(f"\n4. Total records in public.roles: {count}")
            
            # Get sample data
            if count > 0:
                print("\n5. Sample data from public.roles:")
                cursor.execute("SELECT * FROM public.roles ORDER BY id LIMIT 10;")
                roles = cursor.fetchall()
                for role in roles:
                    print(f"   {dict(role)}")
            
            # Check foreign key references
            print("\n6. Foreign key references TO public.roles:")
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND ccu.table_name = 'roles';
            """)
            fk_refs = cursor.fetchall()
            if fk_refs:
                for ref in fk_refs:
                    print(f"   - {ref['table_name']}.{ref['column_name']} -> "
                          f"{ref['foreign_table_name']}.{ref['foreign_column_name']}")
            else:
                print("   No foreign key references found")
        
        # Analyze public.hrm_roles
        if hrm_roles_exists:
            print("\n" + "=" * 80)
            print("ANALYZING public.hrm_roles TABLE")
            print("=" * 80)
            
            # Get table structure
            print("\n7. Structure of public.hrm_roles:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'hrm_roles'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} "
                      f"(nullable: {col['is_nullable']}, default: {col['column_default']})")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) as count FROM public.hrm_roles;")
            count = cursor.fetchone()['count']
            print(f"\n8. Total records in public.hrm_roles: {count}")
            
            # Get sample data
            if count > 0:
                print("\n9. Sample data from public.hrm_roles:")
                cursor.execute("SELECT * FROM public.hrm_roles ORDER BY id LIMIT 10;")
                roles = cursor.fetchall()
                for role in roles:
                    print(f"   {dict(role)}")
            
            # Check foreign key references
            print("\n10. Foreign key references TO public.hrm_roles:")
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND ccu.table_name = 'hrm_roles';
            """)
            fk_refs = cursor.fetchall()
            if fk_refs:
                for ref in fk_refs:
                    print(f"   - {ref['table_name']}.{ref['column_name']} -> "
                          f"{ref['foreign_table_name']}.{ref['foreign_column_name']}")
            else:
                print("   No foreign key references found")
        
        # Compare data if both tables exist
        if roles_exists and hrm_roles_exists:
            print("\n" + "=" * 80)
            print("COMPARING DATA BETWEEN TABLES")
            print("=" * 80)
            
            # Check for overlapping role names
            print("\n11. Checking for overlapping role names:")
            cursor.execute("""
                SELECT r.id as roles_id, r.name, hr.id as hrm_roles_id
                FROM public.roles r
                LEFT JOIN public.hrm_roles hr ON r.name = hr.name
                ORDER BY r.id;
            """)
            overlaps = cursor.fetchall()
            if overlaps:
                print("   Role Name Comparison:")
                for overlap in overlaps:
                    status = "EXISTS IN BOTH" if overlap['hrm_roles_id'] else "ONLY IN roles"
                    print(f"   - {overlap['name']} (roles.id={overlap['roles_id']}) -> {status}")
            
            # Check for roles in hrm_roles not in roles
            print("\n12. Roles in hrm_roles but NOT in roles:")
            cursor.execute("""
                SELECT hr.id, hr.name
                FROM public.hrm_roles hr
                LEFT JOIN public.roles r ON hr.name = r.name
                WHERE r.id IS NULL
                ORDER BY hr.id;
            """)
            hrm_only = cursor.fetchall()
            if hrm_only:
                for role in hrm_only:
                    print(f"   - {role['name']} (hrm_roles.id={role['id']})")
            else:
                print("   None found")
        
        # Check hrm_users table references
        print("\n" + "=" * 80)
        print("CHECKING hrm_users TABLE REFERENCES")
        print("=" * 80)
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_users'
            );
        """)
        users_exists = cursor.fetchone()['exists']
        
        if users_exists:
            print("\n13. Checking hrm_users.role_id column:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_users' 
                AND column_name = 'role_id';
            """)
            role_id_col = cursor.fetchone()
            if role_id_col:
                print(f"   - role_id column exists: {role_id_col['data_type']}")
                
                # Check which table it references
                cursor.execute("""
                    SELECT 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                        AND tc.table_name = 'hrm_users'
                        AND kcu.column_name = 'role_id';
                """)
                fk_ref = cursor.fetchone()
                if fk_ref:
                    print(f"   - Foreign key references: {fk_ref['foreign_table_name']}.{fk_ref['foreign_column_name']}")
                else:
                    print("   - No foreign key constraint found")
                
                # Check sample data
                cursor.execute("""
                    SELECT id, username, role_id 
                    FROM hrm_users 
                    ORDER BY id 
                    LIMIT 5;
                """)
                users = cursor.fetchall()
                print("\n14. Sample hrm_users data:")
                for user in users:
                    print(f"   - User {user['id']} ({user['username']}): role_id={user['role_id']}")
            else:
                print("   - role_id column NOT found in hrm_users")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    analyze_tables()