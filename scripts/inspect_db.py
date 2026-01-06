
import sys
import os
from sqlalchemy import text, inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db

def inspect_db():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")
        
        if 'hrm_company' in tables:
            print("hrm_company exists.")
        else:
            print("hrm_company MISSING.")
            
        if 'hrm_holiday' in tables:
            print("hrm_holiday exists.")
        else:
            print("hrm_holiday does NOT exist.")

if __name__ == "__main__":
    inspect_db()
