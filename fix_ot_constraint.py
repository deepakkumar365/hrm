
import os
from flask import Flask
from sqlalchemy import text
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Setup minimal app context
from app import app
from core.models import db

def drop_constraint():
    with app.app_context():
        try:
            print("Attempting to drop constraint 'uq_ot_daily_emp_date'...")
           
            # RAW SQL to drop
            sql = text("ALTER TABLE hrm_ot_daily_summary DROP CONSTRAINT IF EXISTS uq_ot_daily_emp_date;")
            
            # Execute with session
            conn = db.engine.connect()
            trans = conn.begin()
            try:
                conn.execute(sql)
                trans.commit()
                print("Constraint dropped successfully (if it existed).")
            except Exception as sql_err:
                trans.rollback()
                print(f"SQL Error: {sql_err}")
                raise sql_err
            finally:
                conn.close()

        except Exception as e:
            print(f"Error dropping constraint: {e}")

if __name__ == "__main__":
    drop_constraint()
