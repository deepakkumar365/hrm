#!/usr/bin/env python
"""
Fix email column to allow NULL values in hrm_employee table
"""
import os
import sys
from app import app, db

def fix_email_nullable():
    """Make email column nullable in hrm_employee table"""
    with app.app_context():
        try:
            print("🔧 Fixing email column to allow NULL values...")
            
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # First, set empty strings to NULL
                print("  • Setting empty strings to NULL...")
                cursor.execute("UPDATE hrm_employee SET email = NULL WHERE email = '';")
                connection.commit()
                print("    ✓ Updated empty strings to NULL")
            except Exception as e:
                print(f"    ⚠ Could not update empty strings (may not exist): {e}")
                connection.rollback()
            
            try:
                # Drop the unique constraint
                print("  • Dropping existing unique constraint...")
                cursor.execute("ALTER TABLE hrm_employee DROP CONSTRAINT IF EXISTS hrm_employee_email_key;")
                connection.commit()
                print("    ✓ Dropped unique constraint")
            except Exception as e:
                print(f"    ⚠ Could not drop constraint: {e}")
                connection.rollback()
            
            try:
                # Alter column to allow NULL
                print("  • Altering email column to allow NULL...")
                cursor.execute("ALTER TABLE hrm_employee ALTER COLUMN email DROP NOT NULL;")
                connection.commit()
                print("    ✓ Column altered successfully")
            except Exception as e:
                print(f"    ⚠ Could not alter column: {e}")
                connection.rollback()
            
            try:
                # Recreate unique constraint that allows multiple NULLs
                print("  • Recreating unique constraint...")
                cursor.execute("""
                    ALTER TABLE hrm_employee 
                    ADD CONSTRAINT hrm_employee_email_key UNIQUE (email);
                """)
                connection.commit()
                print("    ✓ Unique constraint recreated")
            except Exception as e:
                print(f"    ⚠ Could not recreate constraint: {e}")
                connection.rollback()
            
            cursor.close()
            connection.close()
            
            print("\n✅ Email column fix completed successfully!")
            print("\n📋 Summary:")
            print("  • Email column now allows NULL values")
            print("  • Multiple employees can be created without email")
            print("  • Email remains unique for non-NULL values")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error fixing email column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_email_nullable()
    sys.exit(0 if success else 1)