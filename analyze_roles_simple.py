"""
Simple script to analyze roles tables using Flask app context
"""
from app import app, db
from sqlalchemy import text

def analyze_roles():
    with app.app_context():
        print("=" * 80)
        print("ANALYZING ROLES TABLES")
        print("=" * 80)
        
        # Check if public.roles table exists
        print("\n1. Checking if public.roles table exists...")
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'roles'
            );
        """))
        roles_exists = result.scalar()
        print(f"   public.roles exists: {roles_exists}")
        
        # Check if public.hrm_roles table exists
        print("\n2. Checking if public.hrm_roles table exists...")
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_roles'
            );
        """))
        hrm_roles_exists = result.scalar()
        print(f"   public.hrm_roles exists: {hrm_roles_exists}")
        
        # Analyze public.roles if it exists
        if roles_exists:
            print("\n" + "=" * 80)
            print("ANALYZING public.roles TABLE")
            print("=" * 80)
            
            # Get table structure
            print("\n3. Structure of public.roles:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'roles'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
            # Get row count
            result = db.session.execute(text("SELECT COUNT(*) as count FROM public.roles;"))
            count = result.scalar()
            print(f"\n4. Total records in public.roles: {count}")
            
            # Get sample data
            if count > 0:
                print("\n5. Sample data from public.roles:")
                result = db.session.execute(text("SELECT * FROM public.roles ORDER BY id LIMIT 10;"))
                roles = result.fetchall()
                for role in roles:
                    print(f"   {dict(role._mapping)}")
            
            # Check foreign key references
            print("\n6. Foreign key references TO public.roles:")
            result = db.session.execute(text("""
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
            """))
            fk_refs = result.fetchall()
            if fk_refs:
                for ref in fk_refs:
                    print(f"   - {ref[0]}.{ref[1]} -> {ref[2]}.{ref[3]}")
            else:
                print("   No foreign key references found")
        
        # Analyze public.hrm_roles
        if hrm_roles_exists:
            print("\n" + "=" * 80)
            print("ANALYZING public.hrm_roles TABLE")
            print("=" * 80)
            
            # Get table structure
            print("\n7. Structure of public.hrm_roles:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'hrm_roles'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
            # Get row count
            result = db.session.execute(text("SELECT COUNT(*) as count FROM public.hrm_roles;"))
            count = result.scalar()
            print(f"\n8. Total records in public.hrm_roles: {count}")
            
            # Get sample data
            if count > 0:
                print("\n9. Sample data from public.hrm_roles:")
                result = db.session.execute(text("SELECT * FROM public.hrm_roles ORDER BY id LIMIT 10;"))
                roles = result.fetchall()
                for role in roles:
                    print(f"   {dict(role._mapping)}")
            
            # Check foreign key references
            print("\n10. Foreign key references TO public.hrm_roles:")
            result = db.session.execute(text("""
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
            """))
            fk_refs = result.fetchall()
            if fk_refs:
                for ref in fk_refs:
                    print(f"   - {ref[0]}.{ref[1]} -> {ref[2]}.{ref[3]}")
            else:
                print("   No foreign key references found")
        
        # Compare data if both tables exist
        if roles_exists and hrm_roles_exists:
            print("\n" + "=" * 80)
            print("COMPARING DATA BETWEEN TABLES")
            print("=" * 80)
            
            # Check for overlapping role names
            print("\n11. Checking for overlapping role names:")
            result = db.session.execute(text("""
                SELECT r.id as roles_id, r.name, hr.id as hrm_roles_id
                FROM public.roles r
                LEFT JOIN public.hrm_roles hr ON r.name = hr.name
                ORDER BY r.id;
            """))
            overlaps = result.fetchall()
            if overlaps:
                print("   Role Name Comparison:")
                for overlap in overlaps:
                    status = "EXISTS IN BOTH" if overlap[2] else "ONLY IN roles"
                    print(f"   - {overlap[1]} (roles.id={overlap[0]}) -> {status}")
            
            # Check for roles in hrm_roles not in roles
            print("\n12. Roles in hrm_roles but NOT in roles:")
            result = db.session.execute(text("""
                SELECT hr.id, hr.name
                FROM public.hrm_roles hr
                LEFT JOIN public.roles r ON hr.name = r.name
                WHERE r.id IS NULL
                ORDER BY hr.id;
            """))
            hrm_only = result.fetchall()
            if hrm_only:
                for role in hrm_only:
                    print(f"   - {role[1]} (hrm_roles.id={role[0]})")
            else:
                print("   None found")
        
        # Check hrm_users table references
        print("\n" + "=" * 80)
        print("CHECKING hrm_users TABLE REFERENCES")
        print("=" * 80)
        
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_users'
            );
        """))
        users_exists = result.scalar()
        
        if users_exists:
            print("\n13. Checking hrm_users.role_id column:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'hrm_users' 
                AND column_name = 'role_id';
            """))
            role_id_col = result.fetchone()
            if role_id_col:
                print(f"   - role_id column exists: {role_id_col[1]}")
                
                # Check which table it references
                result = db.session.execute(text("""
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
                """))
                fk_ref = result.fetchone()
                if fk_ref:
                    print(f"   - Foreign key references: {fk_ref[0]}.{fk_ref[1]}")
                else:
                    print("   - No foreign key constraint found")
                
                # Check sample data
                result = db.session.execute(text("""
                    SELECT id, username, role_id 
                    FROM hrm_users 
                    ORDER BY id 
                    LIMIT 5;
                """))
                users = result.fetchall()
                print("\n14. Sample hrm_users data:")
                for user in users:
                    print(f"   - User {user[0]} ({user[1]}): role_id={user[2]}")
            else:
                print("   - role_id column NOT found in hrm_users")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

if __name__ == '__main__':
    try:
        analyze_roles()
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()