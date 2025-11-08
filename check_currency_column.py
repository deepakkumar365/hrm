#!/usr/bin/env python
"""Check if currency_code column exists in hrm_company table"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_column():
    try:
        from main import app, db
        
        with app.app_context():
            from sqlalchemy import text, inspect
            
            # Check if table exists
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("📊 Database Check")
            print("=" * 50)
            
            if 'hrm_company' not in tables:
                print("❌ hrm_company table NOT FOUND")
                return False
            
            print("✅ hrm_company table found")
            
            # Check columns
            columns = inspector.get_columns('hrm_company')
            column_names = [col['name'] for col in columns]
            
            print(f"\n📋 Total columns: {len(column_names)}")
            
            if 'currency_code' in column_names:
                print("✅ currency_code column EXISTS")
                
                # Show column details
                for col in columns:
                    if col['name'] == 'currency_code':
                        print(f"   Type: {col['type']}")
                        print(f"   Nullable: {col['nullable']}")
                        print(f"   Default: {col['default']}")
                
                return True
            else:
                print("❌ currency_code column NOT FOUND")
                print("\n📌 Available columns:")
                for i, col in enumerate(columns, 1):
                    print(f"   {i}. {col['name']}")
                
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n⚠️  Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. DATABASE_URL is set in .env")
        print("   3. App can connect to database")
        return False

if __name__ == "__main__":
    success = check_column()
    print("\n" + "=" * 50)
    if success:
        print("✅ Column check PASSED - Ready to use!")
    else:
        print("❌ Column check FAILED - Migration not applied")
    sys.exit(0 if success else 1)