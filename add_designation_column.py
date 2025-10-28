#!/usr/bin/env python3
"""
Quick fix script to add designation_id column to hrm_employee table
This handles the missing column error
"""

from app import app, db
from sqlalchemy import text

def add_designation_column():
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
                return True
            
            print("  Column doesn't exist yet, adding...")
            
            # Add the column
            print("\n[2/3] Adding designation_id column...")
            db.session.execute(text("""
                ALTER TABLE hrm_employee 
                ADD COLUMN designation_id INTEGER
            """))
            print("✓ Column added")
            
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
            print("\nYou can now:")
            print("  1. Refresh your Flask application")
            print("  2. Navigate to employee form")
            print("  3. Try adding/editing an employee")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERROR: {str(e)}")
            print("\nIf the error mentions 'column already exists', the fix is complete.")
            print("Simply restart your Flask application.")
            return False

if __name__ == '__main__':
    success = add_designation_column()
    exit(0 if success else 1)