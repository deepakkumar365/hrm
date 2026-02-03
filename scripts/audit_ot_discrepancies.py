import os
# Hack to satisfy app.py requirement for PROD_SESSION_SECRET even in dev
os.environ.setdefault('PROD_SESSION_SECRET', 'dev_secret_placeholder')

from app import app, db
from core.models import OTRequest, Employee, OTType, OTAttendance
from sqlalchemy.orm import joinedload
from datetime import datetime
from dateutil.relativedelta import relativedelta

def audit_ot_discrepancies():
    with app.app_context():
        # Get Last Month
        today = datetime.today().date()
        last_month_start = (today.replace(day=1) - relativedelta(months=1))
        last_month_end = today.replace(day=1) - relativedelta(days=1)
        
        print(f"\nEvaluating Discrepancies for Period: {last_month_start} to {last_month_end}")
        
        # We check ALL records, but focus on last month
        requests = db.session.query(OTRequest).options(
            joinedload(OTRequest.ot_type),
            joinedload(OTRequest.employee)
        ).filter(
            OTRequest.ot_date >= last_month_start
            # OTRequest.ot_date <= last_month_end # Optional: Extend to today if needed
        ).order_by(OTRequest.ot_date.desc()).all()
        
        print(f"{'Date':<12} | {'Employee':<20} | {'Type (Mult/Rate)':<20} | {'Qty':<6} | {'Current Amt':<12} | {'Expected (Calculated)':<22} | {'Diff':<10}")
        print("-" * 115)
        
        count_bad = 0
        total_lost_value = 0
        
        for r in requests:
            qty = float(r.requested_hours) if r.requested_hours else 0.0
            current_amt = float(r.amount) if r.amount else 0.0
            
            # Theoretical Calculation based on Type
            # Assuming 'Rate' matches 'Rate Multiplier' (Fixed Rate Logic)
            type_rate = float(r.ot_type.rate_multiplier) if r.ot_type and r.ot_type.rate_multiplier else 0.0
            type_name = r.ot_type.name if r.ot_type else "Unknown"
            
            # EXPECTED: Qty * TypeRate
            expected_amt = round(qty * type_rate, 2)
            
            # Discrepancy Check
            # Only flag if significant difference and Expected > Current (Underpayment risk)
            # User case: System shows $2, Expected $30.
            
            if abs(expected_amt - current_amt) > 0.1:
                diff = expected_amt - current_amt
                count_bad += 1
                total_lost_value += diff
                
                emp_name = f"{r.employee.first_name} {r.employee.last_name}"[:20]
                type_display = f"{type_name} ({type_rate})"
                
                print(f"{str(r.ot_date):<12} | {emp_name:<20} | {type_display:<20} | {qty:<6.2f} | ${current_amt:<11.2f} | ${expected_amt:<21.2f} | ${diff:<9.2f}")

        print("\n" + "="*50)
        print(f"Audit Complete.")
        print(f"Total Discrepancies Found: {count_bad}")
        print(f"Total 'Missing' Value: ${total_lost_value:.2f}")
        print("="*50)
        print("Note: 'Expected' assumes the OT Type Multiplier is the Fixed Dollar Rate per unit.")

if __name__ == "__main__":
    audit_ot_discrepancies()
