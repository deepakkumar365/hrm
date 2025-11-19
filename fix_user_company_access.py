#!/usr/bin/env python
"""
Comprehensive fix for missing hrm_user_company_access table
This script will:
1. Check if the table exists
2. Create it if missing
3. Populate it with initial data if needed
4. Mark the migration as applied
"""

import os
import sys

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_section("FIX: MISSING hrm_user_company_access TABLE")
    
    os.environ['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'development')
    
    try:
        print("\n📦 Importing Flask application...")
        from app import app, db
        from sqlalchemy import text, inspect
        
        with app.app_context():
            # Step 1: Check current state
            print_section("STEP 1: Checking Current Database State")
            
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            table_exists = 'hrm_user_company_access' in tables
            
            if table_exists:
                print("✓ Table 'hrm_user_company_access' already EXISTS")
                count = db.session.execute(text(
                    "SELECT COUNT(*) FROM hrm_user_company_access"
                )).scalar()
                print(f"✓ Table contains {count} records")
                return 0
            else:
                print("✗ Table 'hrm_user_company_access' DOES NOT EXIST")
                print("  This is causing the 'UndefinedTable' error")
            
            # Step 2: Check if required tables exist
            print_section("STEP 2: Checking Prerequisites")
            
            required_tables = {
                'hrm_users': 'Users table',
                'hrm_company': 'Company table',
            }
            
            for table_name, description in required_tables.items():
                if table_name in tables:
                    print(f"✓ {description} ({table_name}) exists")
                else:
                    print(f"✗ {description} ({table_name}) MISSING - cannot create foreign keys")
                    return 1
            
            # Step 3: Create the table
            print_section("STEP 3: Creating hrm_user_company_access Table")
            
            try:
                print("\n  Creating table with columns and constraints...")
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS hrm_user_company_access (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id INTEGER NOT NULL,
                        company_id UUID NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        modified_at TIMESTAMP,
                        
                        CONSTRAINT fk_user_company_access_user 
                            FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
                        CONSTRAINT fk_user_company_access_company 
                            FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
                        CONSTRAINT uq_user_company_access 
                            UNIQUE (user_id, company_id)
                    )
                """))
                print("  ✓ Table created successfully")
                
                print("\n  Creating indexes for performance...")
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_user_company_access_user_id 
                    ON hrm_user_company_access(user_id)
                """))
                print("  ✓ Index on user_id created")
                
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_user_company_access_company_id 
                    ON hrm_user_company_access(company_id)
                """))
                print("  ✓ Index on company_id created")
                
                db.session.commit()
                print("\n✓ Table and indexes created successfully")
                
            except Exception as e:
                error_msg = str(e)
                if 'already exists' in error_msg.lower():
                    print("✓ Table already exists (creation skipped)")
                else:
                    print(f"✗ Error creating table: {error_msg}")
                    db.session.rollback()
                    return 1
            
            # Step 4: Populate with initial data (user-company relationships)
            print_section("STEP 4: Populating Initial Data")
            
            try:
                # Get count of existing records
                existing_count = db.session.execute(text(
                    "SELECT COUNT(*) FROM hrm_user_company_access"
                )).scalar()
                
                if existing_count > 0:
                    print(f"✓ Table already populated with {existing_count} records")
                else:
                    print("  Checking for users without company access...")
                    
                    # Get users who don't have company access entries yet
                    users_without_access = db.session.execute(text("""
                        SELECT u.id, e.company_id
                        FROM hrm_users u
                        LEFT JOIN hrm_employee e ON u.id = e.user_id
                        WHERE e.company_id IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM hrm_user_company_access uca
                            WHERE uca.user_id = u.id AND uca.company_id = e.company_id
                        )
                    """)).fetchall()
                    
                    if users_without_access:
                        print(f"  Found {len(users_without_access)} user-company pairs to add")
                        
                        for user_id, company_id in users_without_access:
                            try:
                                db.session.execute(text("""
                                    INSERT INTO hrm_user_company_access (user_id, company_id)
                                    VALUES (:user_id, :company_id)
                                    ON CONFLICT (user_id, company_id) DO NOTHING
                                """), {'user_id': user_id, 'company_id': str(company_id)})
                            except Exception as e:
                                print(f"    ⚠ Error adding access for user {user_id}: {str(e)[:50]}")
                        
                        db.session.commit()
                        
                        # Recount
                        new_count = db.session.execute(text(
                            "SELECT COUNT(*) FROM hrm_user_company_access"
                        )).scalar()
                        print(f"  ✓ Added {new_count - existing_count} new access records (total: {new_count})")
                    else:
                        print("  ✓ All users already have company access entries")
                        
            except Exception as e:
                print(f"⚠ Error populating data: {str(e)[:100]}")
                # This is not critical, table exists which is the main issue
            
            # Step 5: Update migration tracking
            print_section("STEP 5: Tracking Migration Application")
            
            try:
                # Check if migration is already recorded
                migration_check = db.session.execute(text(
                    "SELECT version_num FROM alembic_version WHERE version_num = 'add_user_company_access'"
                )).scalar()
                
                if not migration_check:
                    print("  Recording 'add_user_company_access' migration as applied...")
                    db.session.execute(text(
                        "INSERT INTO alembic_version (version_num) VALUES ('add_user_company_access')"
                    ))
                    db.session.commit()
                    print("  ✓ Migration recorded")
                else:
                    print("  ✓ Migration already recorded")
                    
            except Exception as e:
                print(f"  ⚠ Could not record migration: {str(e)[:100]}")
            
            # Step 6: Final verification
            print_section("STEP 6: Final Verification")
            
            try:
                # Verify table exists
                inspector = inspect(db.engine)
                if 'hrm_user_company_access' in inspector.get_table_names():
                    print("✓ Table 'hrm_user_company_access' verified to exist")
                    
                    # Check columns
                    columns = {col['name'] for col in inspector.get_columns('hrm_user_company_access')}
                    required_cols = {'id', 'user_id', 'company_id', 'created_at'}
                    if required_cols.issubset(columns):
                        print("✓ All required columns present")
                    else:
                        print(f"⚠ Missing columns: {required_cols - columns}")
                    
                    # Count records
                    count = db.session.execute(text(
                        "SELECT COUNT(*) FROM hrm_user_company_access"
                    )).scalar()
                    print(f"✓ Table contains {count} records")
                    
                    print_section("✅ SUCCESS!")
                    print("The hrm_user_company_access table has been created and configured.")
                    print("The 'Bulk Attendance' menu should now work without errors.")
                    return 0
                else:
                    print("✗ Table verification failed")
                    return 1
                    
            except Exception as e:
                print(f"✗ Verification error: {e}")
                return 1
                
    except ImportError as e:
        print(f"\n❌ Error: Missing dependencies")
        print(f"   {e}")
        print("\nPlease install Flask dependencies:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())