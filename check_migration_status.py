"""Quick script to check migration status"""
import sys
from app import app, db
from sqlalchemy import text, inspect

def check_status():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\n" + "="*60)
        print("MIGRATION STATUS CHECK")
        print("="*60)
        
        # Check if tables exist
        has_role = 'role' in tables
        has_hrm_roles = 'hrm_roles' in tables
        
        print(f"\n📋 Table Status:")
        print(f"  - 'role' table exists: {'✅ YES' if has_role else '❌ NO'}")
        print(f"  - 'hrm_roles' table exists: {'✅ YES' if has_hrm_roles else '❌ NO'}")
        
        # Count records in each table
        if has_role:
            try:
                result = db.session.execute(text("SELECT COUNT(*) FROM role"))
                role_count = result.scalar()
                print(f"\n📊 Data in 'role' table: {role_count} records")
                
                # Show sample data
                result = db.session.execute(text("SELECT id, name FROM role LIMIT 5"))
                roles = result.fetchall()
                if roles:
                    print(f"\n  Sample roles:")
                    for role in roles:
                        print(f"    - ID {role[0]}: {role[1]}")
            except Exception as e:
                print(f"  ⚠️  Error reading 'role' table: {e}")
        
        if has_hrm_roles:
            try:
                result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
                hrm_roles_count = result.scalar()
                print(f"\n📊 Data in 'hrm_roles' table: {hrm_roles_count} records")
                
                if hrm_roles_count > 0:
                    # Show sample data
                    result = db.session.execute(text("SELECT id, name FROM hrm_roles LIMIT 5"))
                    roles = result.fetchall()
                    print(f"\n  Sample roles:")
                    for role in roles:
                        print(f"    - ID {role[0]}: {role[1]}")
            except Exception as e:
                print(f"  ⚠️  Error reading 'hrm_roles' table: {e}")
        
        # Check foreign key on hrm_users
        print(f"\n🔗 Foreign Key Status:")
        try:
            result = db.session.execute(text("""
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
            """))
            fk = result.fetchone()
            if fk:
                print(f"  - hrm_users.role_id → {fk[2]}.{fk[3]}")
            else:
                print(f"  - No foreign key found on hrm_users.role_id")
        except Exception as e:
            print(f"  ⚠️  Error checking foreign key: {e}")
        
        print("\n" + "="*60)
        print("MIGRATION NEEDED:")
        print("="*60)
        
        if has_role and not has_hrm_roles:
            print("❌ Migration NOT started")
            print("   → Run: python migrate_roles_table.py")
        elif has_role and has_hrm_roles:
            print("⚠️  Migration IN PROGRESS or INCOMPLETE")
            print("   → Both tables exist. Check data and complete migration.")
        elif not has_role and has_hrm_roles:
            print("✅ Migration COMPLETE")
            print("   → Old 'role' table removed, using 'hrm_roles'")
        else:
            print("❌ ERROR: No role tables found!")
        
        print("="*60 + "\n")

if __name__ == '__main__':
    try:
        check_status()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)