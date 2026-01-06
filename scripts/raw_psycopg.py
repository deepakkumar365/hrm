
import sys
import os
import psycopg2
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db

def run_raw_migration():
    print("🚀 Raw psycopg2 Migration...")
    with app.app_context():
        db_url = str(db.engine.url)
        print(f"Connecting to DB... (host implied from URL)")
        
        # Parse URL or use db.engine.raw_connection()
        try:
            conn = db.engine.raw_connection()
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # 1. Holiday Table
            print("1. Creating hrm_holiday...")
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS hrm_holiday (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    type VARCHAR(20) DEFAULT 'National',
                    company_id UUID REFERENCES hrm_company(id),
                    is_optional BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
                )
                """)
                print("   ✅ Created.")
            except Exception as e:
                print(f"   ⚠️ Error: {e}")

            # 2. WorkingHours Columns
            print("2. Adding columns...")
            cols = [
                ("grace_period", "INTEGER DEFAULT 15"),
                ("late_mark_after_minutes", "INTEGER DEFAULT 15"),
                ("half_day_threshold", "INTEGER DEFAULT 240"),
                ("full_day_threshold", "INTEGER DEFAULT 480"),
                ("weekend_days", "VARCHAR(20) DEFAULT '5,6'")
            ]
            for col_name, col_def in cols:
                try:
                    cursor.execute(f"ALTER TABLE hrm_working_hours ADD COLUMN IF NOT EXISTS {col_name} {col_def}")
                    print(f"   - Added {col_name}")
                except Exception as e:
                    print(f"   - Error {col_name}: {e}")

            # 3. Enum
            print("3. Updating Enum...")
            new_values = ['Half Day', 'Weekly Off', 'Holiday', 'On Duty']
            for val in new_values:
                try:
                    cursor.execute(f"ALTER TYPE attendance_status_enum ADD VALUE IF NOT EXISTS '{val}'")
                    print(f"   - Added {val}")
                except Exception as e:
                    print(f"   - Error {val}: {e}")

            conn.close()
            print("✅ DONE.")
            
        except Exception as e:
            print(f"❌ Connection/Fatal Error: {e}")

if __name__ == "__main__":
    run_raw_migration()
