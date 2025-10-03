"""
Migration script to add is_active column to role table
Run this script once to update the database schema
"""
from app import app, db
from sqlalchemy import text

def add_role_is_active_column():
    """Add is_active column to role table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='role' AND column_name='is_active'
            """))
            
            if result.fetchone():
                print("✓ Column 'is_active' already exists in 'role' table")
                return
            
            # Add the is_active column with default value True
            print("Adding 'is_active' column to 'role' table...")
            db.session.execute(text("""
                ALTER TABLE role 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """))
            
            # Update all existing roles to be active
            db.session.execute(text("""
                UPDATE role 
                SET is_active = TRUE 
                WHERE is_active IS NULL
            """))
            
            db.session.commit()
            print("✓ Successfully added 'is_active' column to 'role' table")
            print("✓ All existing roles set to active")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding column: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Role Table Migration: Adding is_active Column")
    print("=" * 60)
    add_role_is_active_column()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)