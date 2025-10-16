"""
Standalone script to migrate role table to hrm_roles table
This script can be run directly without using Alembic
"""
import os
os.environ['FLASK_SKIP_DB_INIT'] = '1'

from app import app, db
from sqlalchemy import text, inspect
import sys

def migrate_role_to_hrm_roles():
    """Migrate data from role table to hrm_roles table"""
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("=" * 60)
            print("ROLE TABLE MIGRATION TO HRM_ROLES")
            print("=" * 60)
            
            # Check current state
            print("\n📋 Checking current database state...")
            print(f"   - role table exists: {'role' in tables}")
            print(f"   - hrm_roles table exists: {'hrm_roles' in tables}")
            
            if 'role' not in tables:
                print("\n⚠️  ERROR: role table does not exist!")
                print("   Nothing to migrate.")
                return False
            
            if 'hrm_roles' in tables:
                print("\n⚠️  WARNING: hrm_roles table already exists!")
                response = input("   Do you want to continue? This will merge data. (yes/no): ")
                if response.lower() != 'yes':
                    print("   Migration cancelled.")
                    return False
            
            # Count records in role table
            result = db.session.execute(text('SELECT COUNT(*) FROM role'))
            role_count = result.scalar()
            print(f"\n📊 Found {role_count} roles in the role table")
            
            if role_count > 0:
                print("\n   Current roles:")
                result = db.session.execute(text('SELECT id, name, description, is_active FROM role ORDER BY id'))
                for row in result:
                    print(f"      - ID: {row[0]}, Name: {row[1]}, Active: {row[3]}")
            
            # Check users with roles
            result = db.session.execute(text('SELECT COUNT(*) FROM hrm_users WHERE role_id IS NOT NULL'))
            user_count = result.scalar()
            print(f"\n👥 Found {user_count} users with role assignments")
            
            # Confirm migration
            print("\n" + "=" * 60)
            print("⚠️  MIGRATION PLAN:")
            print("   1. Create hrm_roles table (if not exists)")
            print("   2. Copy all data from role to hrm_roles")
            print("   3. Update foreign key constraint in hrm_users")
            print("   4. Drop the old role table")
            print("=" * 60)
            
            response = input("\n🚀 Proceed with migration? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return False
            
            print("\n🔄 Starting migration...\n")
            
            # Step 1: Create hrm_roles table
            print("Step 1: Creating hrm_roles table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS hrm_roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("   ✅ hrm_roles table created")
            
            # Step 2: Migrate data
            print("\nStep 2: Migrating data from role to hrm_roles...")
            db.session.execute(text("""
                INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
                SELECT id, name, description, is_active, created_at, updated_at
                FROM role
                ON CONFLICT (id) DO NOTHING
            """))
            db.session.commit()
            
            # Update sequence
            db.session.execute(text("""
                SELECT setval('hrm_roles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM hrm_roles), true)
            """))
            db.session.commit()
            
            result = db.session.execute(text('SELECT COUNT(*) FROM hrm_roles'))
            migrated_count = result.scalar()
            print(f"   ✅ Migrated {migrated_count} roles")
            
            # Step 3: Update foreign key constraint
            print("\nStep 3: Updating foreign key constraints...")
            
            # Drop old constraint
            try:
                db.session.execute(text("""
                    ALTER TABLE hrm_users DROP CONSTRAINT IF EXISTS hrm_users_role_id_fkey
                """))
                db.session.commit()
                print("   ✅ Dropped old foreign key constraint")
            except Exception as e:
                print(f"   ⚠️  Note: {e}")
                db.session.rollback()
            
            # Add new constraint
            db.session.execute(text("""
                ALTER TABLE hrm_users 
                ADD CONSTRAINT hrm_users_role_id_fkey 
                FOREIGN KEY (role_id) REFERENCES hrm_roles(id)
            """))
            db.session.commit()
            print("   ✅ Added new foreign key constraint to hrm_roles")
            
            # Step 4: Create indexes
            print("\nStep 4: Creating indexes...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hrm_roles_name ON hrm_roles(name)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active ON hrm_roles(is_active)
            """))
            db.session.commit()
            print("   ✅ Indexes created")
            
            # Step 5: Drop old table
            print("\nStep 5: Dropping old role table...")
            db.session.execute(text("DROP TABLE IF EXISTS role CASCADE"))
            db.session.commit()
            print("   ✅ Old role table dropped")
            
            # Verification
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            print("\n📊 Verification:")
            result = db.session.execute(text('SELECT COUNT(*) FROM hrm_roles'))
            print(f"   - Total roles in hrm_roles: {result.scalar()}")
            
            result = db.session.execute(text('SELECT COUNT(*) FROM hrm_users WHERE role_id IS NOT NULL'))
            print(f"   - Users with roles: {result.scalar()}")
            
            print("\n   Roles in hrm_roles table:")
            result = db.session.execute(text('SELECT id, name, description, is_active FROM hrm_roles ORDER BY id'))
            for row in result:
                print(f"      - ID: {row[0]}, Name: {row[1]}, Active: {row[3]}")
            
            print("\n✅ All data successfully migrated to hrm_roles table!")
            print("   The system is now using the hrm_roles table.")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR during migration: {e}")
            print("   Rolling back changes...")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("HRMS ROLE TABLE MIGRATION SCRIPT")
    print("=" * 60)
    print("\nThis script will migrate the 'role' table to 'hrm_roles' table.")
    print("All data will be preserved and foreign key references will be updated.")
    print("\n⚠️  IMPORTANT: Make sure you have a database backup before proceeding!")
    print("=" * 60)
    
    response = input("\nDo you have a database backup? (yes/no): ")
    if response.lower() != 'yes':
        print("\n⚠️  Please create a database backup first!")
        print("   You can use: pg_dump -U username -d database_name > backup.sql")
        sys.exit(1)
    
    success = migrate_role_to_hrm_roles()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("   You can now restart your application.")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above.")
        sys.exit(1)