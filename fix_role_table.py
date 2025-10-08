"""
Script to add missing columns to role table
"""
import os
os.environ['FLASK_SKIP_DB_INIT'] = '1'

from app import app, db

def fix_role_table():
    """Add missing columns to role table"""
    print("🔄 Adding missing columns to role table...")
    
    sql_statements = [
        # Add is_active column if it doesn't exist
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'role' AND column_name = 'is_active'
            ) THEN
                ALTER TABLE role ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
                RAISE NOTICE 'Added is_active column to role table';
            ELSE
                RAISE NOTICE 'is_active column already exists in role table';
            END IF;
        END $$;
        """,
        # Add created_at column if it doesn't exist
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'role' AND column_name = 'created_at'
            ) THEN
                ALTER TABLE role ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
                RAISE NOTICE 'Added created_at column to role table';
            ELSE
                RAISE NOTICE 'created_at column already exists in role table';
            END IF;
        END $$;
        """,
        # Add updated_at column if it doesn't exist
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'role' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE role ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
                RAISE NOTICE 'Added updated_at column to role table';
            ELSE
                RAISE NOTICE 'updated_at column already exists in role table';
            END IF;
        END $$;
        """
    ]
    
    try:
        for sql in sql_statements:
            db.session.execute(db.text(sql))
        db.session.commit()
        print("✅ Role table fixed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error fixing role table: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    import sys
    
    with app.app_context():
        if fix_role_table():
            print("\n✅ Migration completed successfully!")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)