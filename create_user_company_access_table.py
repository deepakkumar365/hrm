#!/usr/bin/env python
"""Direct SQL script to create hrm_user_company_access table"""

import os
import sys

def main():
    print("=" * 70)
    print("CREATING USER COMPANY ACCESS TABLE (DIRECT SQL)")
    print("=" * 70)
    
    os.environ['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'development')
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            print("\n🔍 Checking if table already exists...")
            
            # Check if table exists
            check_table = db.session.execute(text(
                "SELECT to_regclass('hrm_user_company_access')"
            )).scalar()
            
            if check_table:
                print("✓ Table 'hrm_user_company_access' already exists")
                return 0
            
            print("✗ Table does not exist - creating now...")
            
            # SQL to create the table
            sql_statements = [
                # Create the table
                """
                CREATE TABLE IF NOT EXISTS hrm_user_company_access (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id INTEGER NOT NULL,
                    company_id UUID NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    modified_at TIMESTAMP,
                    
                    CONSTRAINT fk_user_company_access_user 
                        FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
                    CONSTRAINT fk_user_company_access_company 
                        FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
                    CONSTRAINT uq_user_company_access 
                        UNIQUE (user_id, company_id)
                )
                """,
                
                # Create indexes
                "CREATE INDEX IF NOT EXISTS ix_user_company_access_user_id ON hrm_user_company_access(user_id)",
                "CREATE INDEX IF NOT EXISTS ix_user_company_access_company_id ON hrm_user_company_access(company_id)",
            ]
            
            for i, sql in enumerate(sql_statements, 1):
                try:
                    print(f"\n  Executing statement {i}...")
                    db.session.execute(text(sql))
                    print(f"  ✓ Statement {i} executed successfully")
                except Exception as e:
                    print(f"  ⚠ Statement {i} note: {str(e)[:100]}")
            
            # Commit changes
            db.session.commit()
            print("\n✓ All changes committed")
            
            # Mark migration as applied in alembic_version
            print("\n📝 Marking migration as applied in alembic_version...")
            try:
                # Check if migration is already recorded
                result = db.session.execute(text(
                    "SELECT version_num FROM alembic_version WHERE version_num = 'add_user_company_access'"
                )).scalar()
                
                if not result:
                    db.session.execute(text(
                        "INSERT INTO alembic_version (version_num) VALUES ('add_user_company_access')"
                    ))
                    db.session.commit()
                    print("✓ Migration recorded in alembic_version")
                else:
                    print("✓ Migration already recorded in alembic_version")
            except Exception as e:
                print(f"⚠ Could not record migration: {e}")
            
            # Final verification
            print("\n🔍 Verifying table creation...")
            check_table = db.session.execute(text(
                "SELECT to_regclass('hrm_user_company_access')"
            )).scalar()
            
            if check_table:
                count = db.session.execute(text(
                    "SELECT COUNT(*) FROM hrm_user_company_access"
                )).scalar()
                print(f"✓ Table 'hrm_user_company_access' exists with {count} rows")
                print("\n✅ SUCCESS! Table has been created successfully")
                return 0
            else:
                print("✗ Table creation failed")
                return 1
                
    except ImportError as e:
        print(f"\n❌ Error: Missing dependencies: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())