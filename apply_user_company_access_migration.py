#!/usr/bin/env python
"""Apply the user_company_access migration to fix the missing table"""

import os
import sys

def main():
    print("=" * 70)
    print("APPLYING USER COMPANY ACCESS MIGRATION")
    print("=" * 70)
    
    # Set environment for Flask
    os.environ['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'development')
    
    try:
        # Import Flask app
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            # Check current applied migrations
            print("\n📋 Checking current migrations...")
            try:
                result = db.session.execute(text(
                    "SELECT version_num FROM alembic_version ORDER BY version_num"
                )).fetchall()
                applied = [r[0] for r in result]
                print(f"✓ Found {len(applied)} applied migrations")
                
                if 'add_user_company_access' in applied:
                    print("✓ Migration 'add_user_company_access' is already applied")
                    return 0
                else:
                    print("✗ Migration 'add_user_company_access' is NOT applied - will apply now")
            except Exception as e:
                print(f"⚠ Could not check applied migrations: {e}")
            
            # Apply the migration using Flask-Migrate
            print("\n⚙️  Running Flask-Migrate upgrade...")
            from flask_migrate import Migrate, upgrade
            
            # Initialize migrate
            migrate = Migrate(app, db)
            
            # Run upgrade to latest
            upgrade()
            
            print("\n✓ Migration upgrade completed successfully")
            
            # Verify the table was created
            print("\n🔍 Verifying table creation...")
            try:
                # Check if table exists
                inspector_result = db.session.execute(text(
                    "SELECT to_regclass('hrm_user_company_access')"
                )).scalar()
                
                if inspector_result:
                    print("✓ Table 'hrm_user_company_access' exists")
                    
                    # Count rows
                    count = db.session.execute(text(
                        "SELECT COUNT(*) FROM hrm_user_company_access"
                    )).scalar()
                    print(f"✓ Table has {count} rows")
                    
                    print("\n✅ SUCCESS! The hrm_user_company_access table is now available")
                    return 0
                else:
                    print("✗ Table 'hrm_user_company_access' still does not exist")
                    return 1
                    
            except Exception as e:
                print(f"⚠ Error verifying table: {e}")
                return 1
                
    except ImportError as e:
        print(f"\n❌ Error: Could not import Flask dependencies: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())