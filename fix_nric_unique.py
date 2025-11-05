#!/usr/bin/env python
"""
Fix NRIC unique constraint to allow multiple NULL values
This script removes the unique constraint and creates a partial unique index instead
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app import db, create_app

def fix_nric_constraint():
    """Fix the NRIC unique constraint in the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get raw connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("🔧 Fixing NRIC unique constraint...")
            
            # Step 1: Drop existing unique constraint if it exists
            print("   Step 1: Removing old unique constraint...")
            try:
                cursor.execute('''
                    ALTER TABLE hrm_employee 
                    DROP CONSTRAINT IF EXISTS hrm_employee_nric_key CASCADE
                ''')
                connection.commit()
                print("   ✓ Old constraint dropped")
            except Exception as e:
                print(f"   ℹ No old constraint to drop: {e}")
                connection.rollback()
            
            # Step 2: Create partial unique index (allows multiple NULLs)
            print("   Step 2: Creating partial unique index...")
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_nric_unique_partial 
                ON hrm_employee(nric) 
                WHERE nric IS NOT NULL
            ''')
            connection.commit()
            print("   ✓ Partial unique index created")
            
            cursor.close()
            connection.close()
            
            print("\n✅ SUCCESS! NRIC field now accepts multiple NULL values")
            print("   - NULL values (empty NRIC) can be added multiple times")
            print("   - Non-NULL values remain unique")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = fix_nric_constraint()
    sys.exit(0 if success else 1)