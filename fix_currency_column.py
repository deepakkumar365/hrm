#!/usr/bin/env python
"""Quick fix to add missing currency_code column to hrm_company table"""

import sys
import os
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db

def add_currency_column():
    """Add currency_code column to hrm_company table if it doesn't exist"""
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('hrm_company')]
            
            if 'currency_code' in columns:
                print("✅ Column 'currency_code' already exists in hrm_company table")
                return True
            
            print("⏳ Adding currency_code column to hrm_company table...")
            
            # Add the column
            with db.engine.connect() as connection:
                # PostgreSQL syntax
                connection.execute(text("""
                    ALTER TABLE hrm_company 
                    ADD COLUMN currency_code VARCHAR(10) NOT NULL DEFAULT 'SGD'
                """))
                connection.commit()
            
            print("✅ Successfully added currency_code column to hrm_company")
            print("   - Column type: VARCHAR(10)")
            print("   - Default value: 'SGD'")
            print("   - Nullable: NO")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding column: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 DATABASE SCHEMA FIX: Adding Missing currency_code Column")
    print("=" * 60)
    print()
    
    success = add_currency_column()
    
    print()
    if success:
        print("=" * 60)
        print("✅ FIX COMPLETE - Database is now ready!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ FIX FAILED - Please check the error above")
        print("=" * 60)
        sys.exit(1)