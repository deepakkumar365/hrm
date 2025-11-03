#!/usr/bin/env python
"""
Add is_manager column to hrm_employee table to track employees who can be reporting managers
"""
import os
import sys
from app import app, db

def fix_is_manager_column():
    """Add is_manager column to hrm_employee table"""
    with app.app_context():
        try:
            print("🔧 Adding is_manager column to hrm_employee table...")
            
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # Check if column already exists
                print("  • Checking if is_manager column exists...")
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='hrm_employee' AND column_name='is_manager';
                """)
                
                if cursor.fetchone():
                    print("    ✓ Column already exists, skipping creation")
                    cursor.close()
                    connection.close()
                    return True
                
                # Add the column
                print("  • Adding is_manager column with default value false...")
                cursor.execute("""
                    ALTER TABLE hrm_employee 
                    ADD COLUMN is_manager BOOLEAN NOT NULL DEFAULT false;
                """)
                connection.commit()
                print("    ✓ Column added successfully")
                
            except Exception as e:
                print(f"    ⚠ Error adding column: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
                connection.close()
            
            print("\n✅ is_manager column fix completed successfully!")
            print("\n📋 Summary:")
            print("  • Added is_manager boolean column to hrm_employee")
            print("  • Default value is False for existing employees")
            print("  • Only employees with is_manager=True will appear in Reporting Manager dropdown")
            print("\n📝 Next steps:")
            print("  • Go to employee edit form")
            print("  • Check 'Can be Reporting Manager' for employees who should be managers")
            print("  • Save the employee")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error adding is_manager column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_is_manager_column()
    sys.exit(0 if success else 1)