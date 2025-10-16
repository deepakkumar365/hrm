"""
Direct Migration Script - Migrate role table to hrm_roles
Run this to migrate your data NOW
"""
import sys
from app import app, db
from sqlalchemy import text, inspect

def migrate():
    print("\n" + "="*70)
    print("ROLE TABLE MIGRATION: role → hrm_roles")
    print("="*70)
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Step 1: Check current state
        print("\n[1/7] Checking current state...")
        has_role = 'role' in tables
        has_hrm_roles = 'hrm_roles' in tables
        
        if not has_role:
            print("❌ ERROR: 'role' table not found!")
            print("   Nothing to migrate.")
            return False
        
        # Count records
        result = db.session.execute(text("SELECT COUNT(*) FROM role"))
        role_count = result.scalar()
        print(f"✅ Found 'role' table with {role_count} records")
        
        if role_count == 0:
            print("⚠️  WARNING: 'role' table is empty!")
            print("   Nothing to migrate.")
            return False
        
        # Show what will be migrated
        print(f"\n📋 Roles to migrate:")
        result = db.session.execute(text("SELECT id, name FROM role ORDER BY id"))
        roles = result.fetchall()
        for role in roles:
            print(f"   - ID {role[0]}: {role[1]}")
        
        # Step 2: Create hrm_roles table if it doesn't exist
        print(f"\n[2/7] Creating 'hrm_roles' table...")
        if has_hrm_roles:
            print("⚠️  'hrm_roles' table already exists")
            result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
            existing_count = result.scalar()
            if existing_count > 0:
                print(f"   It has {existing_count} records")
                response = input("\n⚠️  Drop and recreate? (yes/no): ").strip().lower()
                if response != 'yes':
                    print("❌ Migration cancelled")
                    return False
                print("   Dropping hrm_roles table...")
                db.session.execute(text("DROP TABLE IF EXISTS hrm_roles CASCADE"))
                db.session.commit()
        
        print("   Creating hrm_roles table...")
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
        print("✅ Table created")
        
        # Step 3: Copy data
        print(f"\n[3/7] Copying {role_count} records from 'role' to 'hrm_roles'...")
        db.session.execute(text("""
            INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
            SELECT id, name, description, is_active, created_at, updated_at
            FROM role
            ORDER BY id
        """))
        db.session.commit()
        
        # Verify copy
        result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
        copied_count = result.scalar()
        print(f"✅ Copied {copied_count} records")
        
        if copied_count != role_count:
            print(f"❌ ERROR: Record count mismatch!")
            print(f"   Expected: {role_count}, Got: {copied_count}")
            return False
        
        # Step 4: Update sequence
        print(f"\n[4/7] Updating sequence...")
        db.session.execute(text("""
            SELECT setval('hrm_roles_id_seq', 
                         (SELECT MAX(id) FROM hrm_roles))
        """))
        db.session.commit()
        print("✅ Sequence updated")
        
        # Step 5: Update foreign key
        print(f"\n[5/7] Updating foreign key on hrm_users...")
        
        # Drop old constraint if exists
        try:
            db.session.execute(text("""
                ALTER TABLE hrm_users 
                DROP CONSTRAINT IF EXISTS hrm_users_role_id_fkey
            """))
            db.session.commit()
            print("   Dropped old constraint")
        except Exception as e:
            print(f"   No old constraint to drop")
        
        # Add new constraint
        db.session.execute(text("""
            ALTER TABLE hrm_users
            ADD CONSTRAINT hrm_users_role_id_fkey
            FOREIGN KEY (role_id) REFERENCES hrm_roles(id)
        """))
        db.session.commit()
        print("✅ Foreign key updated to point to hrm_roles")
        
        # Step 6: Create indexes
        print(f"\n[6/7] Creating indexes...")
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hrm_roles_name 
            ON hrm_roles(name)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active 
            ON hrm_roles(is_active)
        """))
        db.session.commit()
        print("✅ Indexes created")
        
        # Step 7: Drop old table
        print(f"\n[7/7] Dropping old 'role' table...")
        response = input("\n⚠️  Ready to drop 'role' table? (yes/no): ").strip().lower()
        if response == 'yes':
            db.session.execute(text("DROP TABLE role CASCADE"))
            db.session.commit()
            print("✅ Old 'role' table dropped")
        else:
            print("⚠️  Keeping old 'role' table (you can drop it manually later)")
        
        # Final verification
        print(f"\n" + "="*70)
        print("VERIFICATION")
        print("="*70)
        
        result = db.session.execute(text("SELECT COUNT(*) FROM hrm_roles"))
        final_count = result.scalar()
        print(f"✅ hrm_roles table: {final_count} records")
        
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM hrm_users WHERE role_id IS NOT NULL
        """))
        user_count = result.scalar()
        print(f"✅ Users with roles: {user_count}")
        
        print(f"\n" + "="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test role-based functionality")
        print("3. Verify user permissions")
        print("\n")
        
        return True

if __name__ == '__main__':
    try:
        print("\n⚠️  IMPORTANT: Make sure you have a database backup!")
        response = input("Do you have a backup? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\n❌ Please create a backup first!")
            print("   Run: pg_dump -U your_user -d your_db > backup.sql")
            sys.exit(1)
        
        print("\n")
        success = migrate()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)