
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db

def force_migration():
    print("🚀 Force Migration with AUTOCOMMIT...")
    with app.app_context():
        # Use execution options to force autocommit for DDL
        conn = db.engine.connect().execution_options(isolation_level="AUTOCOMMIT")
        try:
            print("1. Creating hrm_holiday...")
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
                )
            """))
            print("   ✅ Created.")

            print("2. Adding columns to hrm_working_hours...")
            cols = [
                ("grace_period", "INTEGER DEFAULT 15"),
                ("late_mark_after_minutes", "INTEGER DEFAULT 15"),
                ("half_day_threshold", "INTEGER DEFAULT 240"),
                ("full_day_threshold", "INTEGER DEFAULT 480"),
                ("weekend_days", "VARCHAR(20) DEFAULT '5,6'")
            ]
            for col_name, col_def in cols:
                try:
                    conn.execute(text(f"ALTER TABLE hrm_working_hours ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
                    print(f"   - Added {col_name}")
                except Exception as e:
                    print(f"   - Error adding {col_name}: {e}")

            print("3. Updating Enum...")
            new_values = ['Half Day', 'Weekly Off', 'Holiday', 'On Duty']
            for val in new_values:
                try:
                    conn.execute(text(f"ALTER TYPE attendance_status_enum ADD VALUE IF NOT EXISTS '{val}'"))
                    print(f"   - Added {val}")
                except Exception as e:
                    print(f"   - Error adding {val}: {e}")
            
            print("✅ DONE.")
        except Exception as e:
            print(f"❌ FATAL: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    force_migration()
