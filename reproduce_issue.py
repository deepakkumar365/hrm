from app import app, db
from core.models import User, Employee, OTDailySummary, Payroll, PayrollConfiguration
from sqlalchemy import extract
from datetime import date

def check_issue():
    with app.app_context():
        u = User.query.filter_by(username='DEVIT058').first()
        if not u:
            print("User DEVIT058 not found")
            return
            
        emp = u.employee_profile
        month = 1
        year = 2026
        
        print(f"Checking for {u.username} (Emp ID: {emp.id})")
        
        # 1. Check Approved OT
        summaries = OTDailySummary.query.filter_by(employee_id=emp.id, status='Approved').filter(extract('month', OTDailySummary.ot_date)==month, extract('year', OTDailySummary.ot_date)==year).all()
        calc_hours = sum(float(s.ot_hours or 0) for s in summaries)
        calc_amt = sum(float(s.ot_amount or 0) for s in summaries)
        print(f"Calculated from OT Summaries: Hours={calc_hours}, Amount={calc_amt}")
        
        # 2. Check Payroll Record
        payroll = Payroll.query.filter_by(employee_id=emp.id).filter(extract('month', Payroll.pay_period_end)==month, extract('year', Payroll.pay_period_end)==year).first()
        
        if payroll:
            print(f"Payroll Record ({payroll.status}): Hours={payroll.overtime_hours}, Amount={payroll.overtime_pay}")
            if float(payroll.overtime_pay or 0) != calc_amt:
                print("MISMATCH DETECTED: Payroll record has stale OT data.")
            else:
                print("No mismatch.")
        else:
            print("No Payroll record found.")

if __name__ == "__main__":
    check_issue()
