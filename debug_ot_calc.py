
from app import app, db
from core.models import User, Employee, OTDailySummary, PayrollConfiguration
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.ERROR)

def debug_ot():
    with app.app_context():
        # 1. Find User/Employee
        u = User.query.filter_by(username='DEVIT057').first()
        if not u:
            print("User DEVIT057 not found.")
            return
        
        emp = u.employee_profile
        if not emp:
            print("Employee profile not found.")
            return

        print(f"DEBUGGING OT FOR: {u.username} (Emp ID: {emp.id})")
        
        # 2. Check Payroll Configuration
        config = emp.payroll_config
        print(f"--- Payroll Config ---")
        if config:
            print(f"  Basic Salary: {config.basic_salary}")
            print(f"  OT Rate Config: {config.ot_rate_per_hour}")
            print(f"  OT Method: {config.ot_calculation_method}") # if exists
        else:
            print("  NO PAYROLL CONFIG FOUND!")
            
        print(f"  (Employee Model fallback): ")
        print(f"  Basic: {emp.basic_salary}")
        print(f"  Hourly: {emp.hourly_rate}")

        # 3. Check OTDailySummary
        print(f"--- OT Daily Summary (Last 10) ---")
        summaries = OTDailySummary.query.filter_by(employee_id=emp.id).order_by(OTDailySummary.ot_date.desc()).limit(10).all()
        
        if not summaries:
            print("  No OT Daily Summaries found.")
        
        for s in summaries:
            print(f"  Date: {s.ot_date} | Status: {s.status} | Hours: {s.ot_hours} | Rate: {s.ot_rate_per_hour} | Amount: {s.ot_amount} | Allowances: {s.total_allowances}")
            
        # 4. Check Pending Approvals that might have been processed
        # ... logic verified in routes_ot.py

if __name__ == "__main__":
    debug_ot()
