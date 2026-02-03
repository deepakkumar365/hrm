import os
# Hack to satisfy app.py requirement for PROD_SESSION_SECRET even in dev
os.environ.setdefault('PROD_SESSION_SECRET', 'dev_secret_placeholder')
from app import app, db
from core.models import OTRequest, Employee, OTType, OTAttendance
from sqlalchemy.orm import joinedload

def get_ot_data():
    with app.app_context():
        # Query OT Requests (Submitted OTs)
        print(f"Connecting to DB: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1].split('/')[0] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Local/Unknown'}")
        print("\n=== OT REQUESTS (Submitted) ===")
        requests = db.session.query(OTRequest).options(
            joinedload(OTRequest.employee),
            joinedload(OTRequest.ot_type)
        ).all()
        
        if not requests:
            print("No submitted OT requests found.")
        else:
            print(f"{'ID':<5} | {'Date':<12} | {'Employee':<20} | {'Type':<15} | {'Hours/Qty':<10} | {'Amount':<10} | {'Status':<15}")
            print("-" * 100)
            for r in requests:
                emp_name = f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown"
                type_name = r.ot_type.name if r.ot_type else "Unknown"
                print(f"{r.id:<5} | {str(r.ot_date):<12} | {emp_name:<20} | {type_name:<15} | {float(r.requested_hours):<10.2f} | {float(r.amount):<10.2f} | {r.status:<15}")

        print(f"\nTotal Submitted OTs: {len(requests)}")

        # Query OT Attendance (All OTs including Drafts)
        print("\n\n=== OT ATTENDANCE (All Records including Drafts) ===")
        attendance = db.session.query(OTAttendance).options(
            joinedload(OTAttendance.employee),
            joinedload(OTAttendance.ot_type)
        ).order_by(OTAttendance.ot_date.desc()).all()
        
        if not attendance:
            print("No OT attendance records found.")
        else:
            print(f"{'ID':<5} | {'Date':<12} | {'Employee':<20} | {'Type':<15} | {'Qty':<10} | {'Amount':<10} | {'Status':<15}")
            print("-" * 100)
            for a in attendance:
                emp_name = f"{a.employee.first_name} {a.employee.last_name}" if a.employee else "Unknown"
                type_name = a.ot_type.name if a.ot_type else "Unknown"
                qty = float(a.quantity) if a.quantity else (float(a.ot_hours) if a.ot_hours else 0.0)
                amt = float(a.amount) if a.amount else 0.0
                print(f"{a.id:<5} | {str(a.ot_date):<12} | {emp_name:<20} | {type_name:<15} | {qty:<10.2f} | {amt:<10.2f} | {a.status:<15}")

        print(f"\nTotal Attendance Records: {len(attendance)}")

if __name__ == "__main__":
    get_ot_data()
