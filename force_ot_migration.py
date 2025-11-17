#!/usr/bin/env python
"""Force execute OT Daily Summary migration directly"""
import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def force_migrate():
    """Execute migration directly without Flask CLI"""
    try:
        print("🔄 Forcing OT Daily Summary migration...\n")
        
        # Import dependencies
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # Create the table directly
                print("📋 Creating hrm_ot_daily_summary table...")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hrm_ot_daily_summary (
                        id SERIAL PRIMARY KEY,
                        employee_id INTEGER NOT NULL,
                        company_id UUID NOT NULL,
                        ot_request_id INTEGER,
                        ot_date DATE NOT NULL,
                        ot_hours NUMERIC(6, 2) DEFAULT 0 NOT NULL,
                        ot_rate_per_hour NUMERIC(8, 2) DEFAULT 0 NOT NULL,
                        ot_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        kd_and_claim NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        trips NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        sinpost NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        sandstone NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        spx NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        psle NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        manpower NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        stacking NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        dispose NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        night NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        ph NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        sun NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        total_allowances NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        total_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL,
                        status VARCHAR(20) DEFAULT 'Draft' NOT NULL,
                        notes TEXT,
                        created_by VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        modified_by VARCHAR(100),
                        modified_at TIMESTAMP,
                        finalized_at TIMESTAMP,
                        finalized_by VARCHAR(100),
                        FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
                        FOREIGN KEY (employee_id) REFERENCES hrm_employee(id) ON DELETE CASCADE,
                        FOREIGN KEY (ot_request_id) REFERENCES hrm_ot_request(id) ON DELETE SET NULL,
                        UNIQUE (employee_id, ot_date)
                    )
                """)
                print("✅ Table created successfully")
                
                # Create indexes
                print("📋 Creating indexes...")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ot_daily_employee_date ON hrm_ot_daily_summary (employee_id, ot_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ot_daily_status ON hrm_ot_daily_summary (status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ot_daily_company ON hrm_ot_daily_summary (company_id)")
                print("✅ Indexes created successfully")
                
                # Update Alembic version table to mark migration as applied
                print("📋 Updating migration history...")
                cursor.execute("""
                    INSERT INTO alembic_version (version_num) 
                    VALUES ('add_ot_daily_summary_001')
                    ON CONFLICT DO NOTHING
                """)
                print("✅ Migration history updated")
                
                connection.commit()
                print("\n✅✅✅ Migration completed successfully!")
                print("✅ Table 'hrm_ot_daily_summary' has been created")
                print("\n📌 You can now access the OT Payroll Summary Grid at:")
                print("   OT Management > Payroll Summary (Grid)")
                print("\n💡 Refresh the page and try clicking the menu again.\n")
                
                return 0
                
            except Exception as e:
                connection.rollback()
                print(f"❌ Error creating table: {str(e)}")
                raise
            finally:
                cursor.close()
                connection.close()
    
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(force_migrate())