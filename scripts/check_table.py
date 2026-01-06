
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db

def check_table():
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT to_regclass('public.hrm_holiday')"))
            val = result.scalar()
            print(f"hrm_holiday check: {val}")
            
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'hrm_working_hours' AND column_name = 'weekend_days'"))
            val2 = result.scalar()
            print(f"weekend_days column check: {val2}")

if __name__ == "__main__":
    check_table()
