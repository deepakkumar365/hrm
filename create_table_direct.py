#!/usr/bin/env python3
"""
Directly create the hrm_company_employee_id_config table.
This bypasses ORM and creates it directly via SQL.
"""

from app import app, db
from sqlalchemy import text

def create_table_directly():
    with app.app_context():
        print("\n" + "="*80)
        print("CREATING TABLE: hrm_company_employee_id_config")
        print("="*80)
        
        sql_create = """
        CREATE TABLE IF NOT EXISTS hrm_company_employee_id_config (
            id SERIAL PRIMARY KEY,
            company_id UUID NOT NULL UNIQUE,
            last_sequence_number INTEGER NOT NULL DEFAULT 0,
            id_prefix VARCHAR(10) NOT NULL,
            created_by VARCHAR(100) NOT NULL DEFAULT 'system',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            modified_by VARCHAR(100),
            modified_at TIMESTAMP,
            CONSTRAINT fk_company_id FOREIGN KEY (company_id) 
                REFERENCES hrm_company(id) ON DELETE CASCADE
        );
        """
        
        sql_index = """
        CREATE INDEX IF NOT EXISTS idx_company_employee_id_config_company_id 
        ON hrm_company_employee_id_config(company_id);
        """
        
        try:
            print("\n[Step 1] Creating table...")
            db.session.execute(text(sql_create))
            db.session.commit()
            print("✅ Table created successfully!")
            
            print("\n[Step 2] Creating index...")
            db.session.execute(text(sql_index))
            db.session.commit()
            print("✅ Index created successfully!")
            
            # Verify
            print("\n[Step 3] Verifying table creation...")
            result = db.session.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'hrm_company_employee_id_config'"
            ))
            if result.fetchone():
                print("✅ Table verified in database!")
            else:
                print("❌ Table not found after creation!")
                return False
            
            # Get columns
            print("\n[Step 4] Table structure:")
            result = db.session.execute(text(
                """SELECT column_name, data_type, is_nullable 
                   FROM information_schema.columns 
                   WHERE table_name = 'hrm_company_employee_id_config'
                   ORDER BY ordinal_position"""
            ))
            
            print("-" * 80)
            for row in result:
                nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                print(f"  {row[0]:25} {row[1]:20} {nullable}")
            print("-" * 80)
            
            print("\n" + "="*80)
            print("✅ TABLE CREATED SUCCESSFULLY!")
            print("="*80)
            
            print("\n🎯 Next steps:")
            print("   1. Run: python init_company_id_config_now.py")
            print("   2. This will initialize configs for all your companies")
            print("   3. Your employee ID sequences will be preserved!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_table_directly()
    exit(0 if success else 1)