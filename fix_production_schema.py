"""
Manual script to fix the production database schema
This script removes the old 'role' column from hrm_users table if it exists
Run this on Render using: python fix_production_schema.py
"""
from app import app, db
from sqlalchemy import text, inspect
import sys

def check_and_fix_schema():
    """Check if the 'role' column exists and remove it if found"""
    with app.app_context():
        try:
            # Get database inspector
            inspector = inspect(db.engine)
            
            # Get columns from hrm_users table
            columns = [col['name'] for col in inspector.get_columns('hrm_users')]
            
            print(f"Current columns in hrm_users table: {columns}")
            
            if 'role' in columns:
                print("\n⚠️  Found old 'role' column in hrm_users table!")
                print("Removing the 'role' column...")
                
                # Drop the role column
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE hrm_users DROP COLUMN IF EXISTS role'))
                    conn.commit()
                
                print("✅ Successfully removed 'role' column from hrm_users table")
                
                # Verify the change
                inspector = inspect(db.engine)
                columns_after = [col['name'] for col in inspector.get_columns('hrm_users')]
                print(f"\nColumns after fix: {columns_after}")
                
                if 'role' not in columns_after:
                    print("\n✅ Schema fix completed successfully!")
                    return True
                else:
                    print("\n❌ Failed to remove 'role' column")
                    return False
            else:
                print("\n✅ Schema is correct - no 'role' column found")
                print("The database schema matches the current model")
                return True
                
        except Exception as e:
            print(f"\n❌ Error fixing schema: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Production Database Schema Fix")
    print("=" * 60)
    print("\nThis script will check and fix the hrm_users table schema")
    print("by removing the old 'role' column if it exists.\n")
    
    success = check_and_fix_schema()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All done! Your database schema is now correct.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Schema fix failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)