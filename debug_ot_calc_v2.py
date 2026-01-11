
from app import app, db
from core.models import User, Employee, OTDailySummary, PayrollConfiguration
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.ERROR)

def debug_ot():
    with app.app_context():
        # 1. Find User/Employee
        u = User.query.filter_by(username='DEVIT058').first()
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
            # Use getattr for safety
            print(f"  Basic Salary: {getattr(config, 'basic_salary', 'N/A')}")
            print(f"  OT Rate Config: {getattr(config, 'ot_rate_per_hour', 'N/A')}")
            # Print all attrs to be sure
            # print(f"  All Attrs: {dir(config)}") 
        else:
            print("  NO PAYROLL CONFIG FOUND!")
            
        print(f"  (Employee Model fallback): ")
        print(f"  Basic: {getattr(emp, 'basic_salary', 'N/A')}")
        print(f"  Hourly: {getattr(emp, 'hourly_rate', 'N/A')}")

        # 3. Check OTDailySummary
        print(f"--- OT Daily Summary (Last 10) ---")
        summaries = OTDailySummary.query.filter_by(employee_id=emp.id).order_by(OTDailySummary.ot_date.desc()).limit(10).all()
        
        if not summaries:
            print("  No OT Daily Summaries found.")
        
        for s in summaries:
            print(f"  Date: {s.ot_date} | Status: {s.status} | Hours: {s.ot_hours} | Rate: {s.ot_rate_per_hour} | Amount: {s.ot_amount} | Allowances: {s.total_allowances}")

        # 4. Check OT Requests
        from core.models import OTRequest
        print(f"--- OT Requests (Last 10) ---")
        requests = OTRequest.query.filter_by(employee_id=emp.id).order_by(OTRequest.ot_date.desc()).limit(10).all()
        if not requests:
            print("  No OT Requests found.")
        for r in requests:
            print(f"  Req ID: {r.id} | Date: {r.ot_date} | Status: {r.status} | Requested: {r.requested_hours} | Approved: {r.approved_hours}")

if __name__ == "__main__":
    debug_ot()
