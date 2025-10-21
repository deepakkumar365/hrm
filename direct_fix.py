#!/usr/bin/env python3
"""Direct database fix for missing designation_id column"""
import os
import sys

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from app import app, db
from sqlalchemy import text

def fix_designation_column():
    with app.app_context():
        try:
            print("=" * 70)
            print("ADDING designation_id COLUMN TO hrm_employee TABLE")
            print("=" * 70)
            
            # Check if column already exists
            print("\n[1/3] Checking if column exists...")
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='hrm_employee' AND column_name='designation_id'
            """)).fetchone()
            
            if result:
                print("✓ Column designation_id already exists")
                print("=" * 70)
                return True
            
            print("  Column doesn't exist yet, adding...")
            
            # Add the column
            print("\n[2/3] Adding designation_id column...")
            db.session.execute(text("""
                ALTER TABLE hrm_employee 
                ADD COLUMN designation_id INTEGER
            """))
            print("✓ Column added successfully")
            
            # Add foreign key constraint
            print("\n[3/3] Adding foreign key constraint...")
            try:
                db.session.execute(text("""
                    ALTER TABLE hrm_employee 
                    ADD CONSTRAINT fk_hrm_employee_designation_id 
                    FOREIGN KEY (designation_id) REFERENCES hrm_designation(id)
                """))
                print("✓ Foreign key constraint added")
            except Exception as e:
                if "already exists" in str(e):
                    print("✓ Foreign key constraint already exists")
                else:
                    print(f"⚠ Note: {str(e)}")
            
            db.session.commit()
            
            print("\n" + "=" * 70)
            print("✓ SUCCESS - designation_id column is ready!")
            print("=" * 70)
            print("\nNext steps:")
            print("  1. Restart your Flask application")
            print("  2. The error should be resolved")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_designation_column()
    sys.exit(0 if success else 1)