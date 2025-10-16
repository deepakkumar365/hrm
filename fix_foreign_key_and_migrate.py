"""
Fix Foreign Key and Complete Migration
This script will:
1. Check current state
2. Create hrm_roles table if needed
3. Copy data from role to hrm_roles
4. Drop the OLD foreign key constraint pointing to 'role'
5. Create NEW foreign key constraint pointing to 'hrm_roles'
6. Drop the old 'role' table
"""
import sys
from app import app, db
from sqlalchemy import text, inspect

def fix_and_migrate():
    print("\n" + "="*70)
    print("FIX FOREIGN KEY & COMPLETE MIGRATION")
    print("="*70)
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Step 1: Check current state
        print("\n[STEP 1] Checking current state...")
        has_role = 'role' in tables
        has_hrm_roles = 'hrm_roles' in tables
        
        print(f"  - 'role' table exists: {'YES' if has_role else 'NO'}")
        print(f"  - 'hrm_roles' table exists: {'YES' if has_hrm_roles else 'NO'}")
        
        if not has_role:
            print("\n❌ ERROR: 'role' table not found!")
            return False
        
        # Count records in role table
        result = db.session.execute(text("SELECT COUNT(*) FROM role"))
        role_count = result.scalar()
        print(f"\n📊 Records in 'role' table: {role_count}")
        
        if role_count == 0:
            print("⚠️  WARNING: 'role' table is empty!")
        else:
            print("\n📋 Roles in 'role' table:")
            result = db.session.execute(text("SELECT id, name FROM role ORDER BY id"))
            roles = result.fetchall()
            for role in roles:
                print(f"   - ID {role[0]}: {role[1]}")
        
        # Step 2: Create hrm_roles if it doesn't exist
        print(f"\n[STEP 2] Ensuring 'hrm_roles' table exists...")
        
        if has_hrm_roles:
            result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
            hrm_count = result.scalar()
            print(f"  ✅ 'hrm_roles' already exists with {hrm_count} records")
            
            if hrm_count == 0 and role_count > 0:
                print("  📋 Copying data from 'role' to 'hrm_roles'...")
                db.session.execute(text("""
                    INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
                    SELECT id, name, description, is_active, created_at, updated_at
                    FROM role
                    ORDER BY id
                """))
                db.session.commit()
                
                # Update sequence
                db.session.execute(text("""
                    SELECT setval('hrm_roles_id_seq', 
                                 (SELECT MAX(id) FROM hrm_roles))
                """))
                db.session.commit()
                print(f"  ✅ Copied {role_count} records")
        else:
            print("  📋 Creating 'hrm_roles' table...")
            db.session.execute(text("""
                CREATE TABLE hrm_roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(80) UNIQUE NOT NULL,
                    description VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("  ✅ Table created")
            
            if role_count > 0:
                print("  📋 Copying data...")
                db.session.execute(text("""
                    INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
                    SELECT id, name, description, is_active, created_at, updated_at
                    FROM role
                    ORDER BY id
                """))
                db.session.commit()
                
                # Update sequence
                db.session.execute(text("""
                    SELECT setval('hrm_roles_id_seq', 
                                 (SELECT MAX(id) FROM hrm_roles))
                """))
                db.session.commit()
                print(f"  ✅ Copied {role_count} records")
        
        # Verify data
        result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
        hrm_roles_count = result.scalar()
        print(f"\n✅ 'hrm_roles' now has {hrm_roles_count} records")
        
        # Step 3: Find and drop OLD foreign key constraint
        print(f"\n[STEP 3] Fixing foreign key constraint on 'hrm_users'...")
        
        # Find all foreign key constraints on hrm_users.role_id
        result = db.session.execute(text("""
            SELECT 
                tc.constraint_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'hrm_users' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'role_id'
        """))
        
        constraints = result.fetchall()
        
        if constraints:
            print(f"\n  Found {len(constraints)} foreign key constraint(s):")
            for constraint in constraints:
                constraint_name = constraint[0]
                foreign_table = constraint[1]
                print(f"    - {constraint_name} → {foreign_table}")
                
                # Drop the constraint
                print(f"    Dropping constraint '{constraint_name}'...")
                db.session.execute(text(f"""
                    ALTER TABLE hrm_users 
                    DROP CONSTRAINT IF EXISTS {constraint_name}
                """))
                db.session.commit()
                print(f"    ✅ Dropped")
        else:
            print("  ℹ️  No existing foreign key constraints found")
        
        # Step 4: Create NEW foreign key pointing to hrm_roles
        print(f"\n[STEP 4] Creating new foreign key to 'hrm_roles'...")
        
        try:
            db.session.execute(text("""
                ALTER TABLE hrm_users
                ADD CONSTRAINT hrm_users_role_id_fkey
                FOREIGN KEY (role_id) REFERENCES hrm_roles(id)
            """))
            db.session.commit()
            print("  ✅ New foreign key created: hrm_users.role_id → hrm_roles.id")
        except Exception as e:
            if "already exists" in str(e):
                print("  ℹ️  Foreign key already exists")
                db.session.rollback()
            else:
                raise
        
        # Step 5: Create indexes on hrm_roles
        print(f"\n[STEP 5] Creating indexes on 'hrm_roles'...")
        
        try:
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hrm_roles_name 
                ON hrm_roles(name)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active 
                ON hrm_roles(is_active)
            """))
            db.session.commit()
            print("  ✅ Indexes created")
        except Exception as e:
            print(f"  ℹ️  Indexes may already exist: {e}")
            db.session.rollback()
        
        # Step 6: NOW we can drop the old 'role' table
        print(f"\n[STEP 6] Dropping old 'role' table...")
        print("  ⚠️  The foreign key has been removed, so this should work now!")
        
        try:
            db.session.execute(text("DROP TABLE IF EXISTS role CASCADE"))
            db.session.commit()
            print("  ✅ Old 'role' table dropped successfully!")
        except Exception as e:
            print(f"  ❌ Error dropping table: {e}")
            db.session.rollback()
            return False
        
        # Final verification
        print(f"\n" + "="*70)
        print("FINAL VERIFICATION")
        print("="*70)
        
        # Check tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Table Status:")
        print(f"  - 'role' exists: {'YES ⚠️' if 'role' in tables else 'NO ✅'}")
        print(f"  - 'hrm_roles' exists: {'YES ✅' if 'hrm_roles' in tables else 'NO ❌'}")
        
        # Count records
        if 'hrm_roles' in tables:
            result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
            count = result.scalar()
            print(f"\n📊 Records in 'hrm_roles': {count}")
            
            if count > 0:
                print("\n📋 Roles in 'hrm_roles':")
                result = db.session.execute(text("SELECT id, name FROM hrm_roles ORDER BY id"))
                roles = result.fetchall()
                for role in roles:
                    print(f"   - ID {role[0]}: {role[1]}")
        
        # Check foreign key
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
            WHERE tc.table_name = 'hrm_users' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'role_id'
        """))
        
        fk = result.fetchone()
        if fk:
            print(f"\n🔗 Foreign Key Status:")
            print(f"  ✅ hrm_users.role_id → {fk[1]}.{fk[2]}")
            
            if fk[1] == 'hrm_roles':
                print("\n" + "="*70)
                print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
                print("="*70)
                print("\n🎉 All done! Your system is now using 'hrm_roles' table.")
                print("\nNext steps:")
                print("1. Restart your application")
                print("2. Test login and role-based features")
                print("3. Verify user permissions work correctly")
                print("\n")
                return True
            else:
                print(f"\n⚠️  WARNING: Foreign key points to '{fk[1]}' instead of 'hrm_roles'")
                return False
        else:
            print(f"\n⚠️  WARNING: No foreign key found on hrm_users.role_id")
            return False

if __name__ == '__main__':
    try:
        print("\n" + "="*70)
        print("ROLE TABLE MIGRATION - FOREIGN KEY FIX")
        print("="*70)
        print("\nThis script will:")
        print("1. Copy data from 'role' to 'hrm_roles' (if needed)")
        print("2. Drop the OLD foreign key constraint")
        print("3. Create NEW foreign key pointing to 'hrm_roles'")
        print("4. Drop the old 'role' table")
        print("\n⚠️  IMPORTANT: Make sure you have a database backup!")
        
        response = input("\nReady to proceed? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\n❌ Migration cancelled")
            sys.exit(1)
        
        success = fix_and_migrate()
        
        if success:
            sys.exit(0)
        else:
            print("\n⚠️  Migration completed with warnings. Please review the output above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)