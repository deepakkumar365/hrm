
from app import app, db
from core.models import OTRequest, OTType, Employee, User

def investigate_zero_amount():
    with app.app_context():
        print("--- INVESTIGATION: ZERO AMOUNT OT ---")
        
        # 1. Check OT Type ID 5
        ot_type = OTType.query.get(5)
        if ot_type:
            print(f"OT Type ID 5: {ot_type.name}")
            print(f"  Code: {ot_type.code}")
            print(f"  Multiplier: {ot_type.rate_multiplier}")
            print(f"  Active: {ot_type.is_active}")
        else:
            print("❌ OT Type ID 5 NOT FOUND")

        # 2. Check Employee Ragunath R (DEVIT061)
        # Try to find by multiple means
        emp = Employee.query.filter((Employee.first_name.ilike('%Ragunath%')) | (Employee.employee_id == 'DEVIT061')).first()
        if not emp:
             print("❌ Employee 'Ragunath R' NOT FOUND")
        else:
             print(f"Employee: {emp.first_name} {emp.last_name} (ID: {emp.id})")
             
             # 3. Check Recent OT Requests for this employee
             print("\n--- Recent OT Requests ---")
             reqs = OTRequest.query.filter_by(employee_id=emp.id).order_by(OTRequest.created_at.desc()).limit(5).all()
             
             for r in reqs:
                 print(f"ID: {r.id} | Date: {r.ot_date} | Hours: {r.requested_hours} | Amount: {r.amount} | Status: {r.status}")
                 print(f"  Type: {r.ot_type.name} (Mult: {r.ot_type.rate_multiplier})")
                 print(f"  Created At: {r.created_at}")
                 
if __name__ == "__main__":
    investigate_zero_amount()
