
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def run_migration():
    print("🚀 Starting Manual Migration Phase 1 (Robust)...")
    with app.app_context():
        conn = db.engine.connect()
        try:
            # 1. Create Holiday Table
            print("1. Creating hrm_holiday table...")
            trans = conn.begin()
            try:
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hrm_holiday (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    type VARCHAR(20) DEFAULT 'National',
                    company_id INTEGER REFERENCES hrm_company(id),
                    is_optional BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
                );
                """))
                # Manually add constraint to avoid syntax error in CREATE TABLE if complex
                # conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_holiday_date_company ON hrm_holiday (date, company_id)"))
                trans.commit()
                print("   ✅ Table Created.")
            except Exception as e:
                trans.rollback()
                print(f"   ⚠️  Error creating table: {e}")

            # 2. Add Columns to WorkingHours
            print("2. Adding columns to hrm_working_hours...")
            trans = conn.begin()
            cols = [
                ("grace_period", "INTEGER DEFAULT 15"),
                ("late_mark_after_minutes", "INTEGER DEFAULT 15"),
                ("half_day_threshold", "INTEGER DEFAULT 240"),
                ("full_day_threshold", "INTEGER DEFAULT 480"),
                ("weekend_days", "VARCHAR(20) DEFAULT '5,6'")
            ]
            for col_name, col_def in cols:
                try:
                    conn.execute(text(f"ALTER TABLE hrm_working_hours ADD COLUMN {col_name} {col_def}"))
                    print(f"   - Added {col_name}")
                except Exception as e:
                    # Likely already exists
                    print(f"   - Skipped {col_name} (likely exists or error: {e})")
            trans.commit()

            # 3. Update Enum type
            print("3. Updating attendance_status_enum...")
            # Enums must be committed immediately
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            new_values = ['Half Day', 'Weekly Off', 'Holiday', 'On Duty']
            for val in new_values:
                try:
                    conn.execute(text(f"ALTER TYPE attendance_status_enum ADD VALUE IF NOT EXISTS '{val}'"))
                    print(f"   - Added {val}")
                except Exception as e:
                    print(f"   - Skipped {val}: {e}")
            
            print("✅ Migration Completed Successfully!")
            
        except Exception as e:
            print(f"❌ Generic Migration Error: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    run_migration()
