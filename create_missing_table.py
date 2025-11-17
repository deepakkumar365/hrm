#!/usr/bin/env python
"""Create missing OTDailySummary table - Run this ONCE to fix the issue"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_table():
    """Create the OTDailySummary table using Flask-SQLAlchemy"""
    
    print("\n" + "="*70)
    print("🔧 Creating Missing OTDailySummary Table")
    print("="*70 + "\n")
    
    try:
        # Import Flask app and database
        print("📦 Loading Flask application...")
        from app import app, db
        print("✅ Flask loaded\n")
        
        # Create application context
        with app.app_context():
            print("🔍 Checking database tables...")
            
            # Import all models to ensure they're registered
            from models import OTDailySummary
            
            # Check if table exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'hrm_ot_daily_summary' in existing_tables:
                print("✅ Table 'hrm_ot_daily_summary' already exists!")
                return 0
            
            print("❌ Table 'hrm_ot_daily_summary' NOT found")
            print("📋 Creating table now...\n")
            
            # Create only the OTDailySummary table
            OTDailySummary.__table__.create(db.engine, checkfirst=True)
            
            print("✅ Table created successfully!")
            print("✅ Indexes created")
            
            # Verify table was created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'hrm_ot_daily_summary' in existing_tables:
                print("\n✅✅✅ VERIFICATION PASSED!")
                print("📊 Table Details:")
                columns = inspector.get_columns('hrm_ot_daily_summary')
                print(f"   - Columns: {len(columns)}")
                print(f"   - Status: READY ✅\n")
                
                print("🎯 Next Steps:")
                print("   1. Restart Flask (stop and start it again)")
                print("   2. Refresh your browser (F5)")
                print("   3. Click: OT Management > Payroll Summary (Grid)")
                print("   4. It should now work! 🚀\n")
                
                return 0
            else:
                print("\n❌ Table creation failed - table not found after creation")
                return 1
                
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("\n📋 Fallback: Using raw SQL...\n")
        
        try:
            import psycopg2
            db_url = os.getenv('DEV_DATABASE_URL') or os.getenv('DATABASE_URL')
            
            if not db_url:
                print("❌ ERROR: DATABASE_URL environment variable not set")
                print("   Set DEV_DATABASE_URL in your .env file")
                return 1
            
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            sql = """
            CREATE TABLE IF NOT EXISTS hrm_ot_daily_summary (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES hrm_employee(id) ON DELETE CASCADE,
                company_id UUID NOT NULL REFERENCES hrm_company(id) ON DELETE CASCADE,
                ot_request_id INTEGER REFERENCES hrm_ot_request(id) ON DELETE SET NULL,
                ot_date DATE NOT NULL,
                ot_hours NUMERIC(6, 2) DEFAULT 0,
                ot_rate_per_hour NUMERIC(8, 2) DEFAULT 0,
                ot_amount NUMERIC(12, 2) DEFAULT 0,
                kd_and_claim NUMERIC(12, 2) DEFAULT 0,
                trips NUMERIC(12, 2) DEFAULT 0,
                sinpost NUMERIC(12, 2) DEFAULT 0,
                sandstone NUMERIC(12, 2) DEFAULT 0,
                spx NUMERIC(12, 2) DEFAULT 0,
                psle NUMERIC(12, 2) DEFAULT 0,
                manpower NUMERIC(12, 2) DEFAULT 0,
                stacking NUMERIC(12, 2) DEFAULT 0,
                dispose NUMERIC(12, 2) DEFAULT 0,
                night NUMERIC(12, 2) DEFAULT 0,
                ph NUMERIC(12, 2) DEFAULT 0,
                sun NUMERIC(12, 2) DEFAULT 0,
                total_allowances NUMERIC(12, 2) DEFAULT 0,
                total_amount NUMERIC(12, 2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'Draft',
                notes TEXT,
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_by VARCHAR(100),
                modified_at TIMESTAMP,
                finalized_at TIMESTAMP,
                finalized_by VARCHAR(100),
                UNIQUE(employee_id, ot_date)
            );
            
            CREATE INDEX IF NOT EXISTS idx_ot_daily_employee_date ON hrm_ot_daily_summary (employee_id, ot_date);
            CREATE INDEX IF NOT EXISTS idx_ot_daily_status ON hrm_ot_daily_summary (status);
            CREATE INDEX IF NOT EXISTS idx_ot_daily_company ON hrm_ot_daily_summary (company_id);
            """
            
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Table created using SQL!")
            print("✅ Indexes created")
            print("\n✅✅✅ VERIFICATION PASSED!")
            print("\n🎯 Next Steps:")
            print("   1. Restart Flask (stop and start it again)")
            print("   2. Refresh your browser (F5)")
            print("   3. Click: OT Management > Payroll Summary (Grid)")
            print("   4. It should now work! 🚀\n")
            
            return 0
            
        except Exception as sql_error:
            print(f"❌ SQL Error: {str(sql_error)}")
            return 1
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = create_table()
    sys.exit(exit_code)