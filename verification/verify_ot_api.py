import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import User, Employee, OTRequest, OTAttendance, OTType
from routes.routes_api import generate_token
import json
from datetime import date, datetime

def verify_ot_api_rate():
    with app.app_context():
        print("--- Verifying OT API Rate Logic ---")
        
        # 1. Find a suitable test user (Employee with a Manager)
        # We need an employee who has a manager, and that manager has a user account.
        
        test_employee = None
        users = User.query.all()
        
        for user in users:
            if not user.employee_profile:
                continue
            
            emp = user.employee_profile
            if emp.manager_id:
                # Check if manager exists and has user
                manager = Employee.query.get(emp.manager_id)
                if manager and manager.user_id:
                     test_employee = emp
                     break
        
        if not test_employee:
            print("❌ No suitable test employee found (needs manager with user account).")
            return

        print(f"Testing with Employee: {test_employee.first_name} (ID: {test_employee.id})")
        print(f"User ID: {test_employee.user_id}")
        
        # 2. Generate Token
        token = generate_token(test_employee.user_id)
        if not token:
             print("❌ Failed to generate token.")
             return
             
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 3. Find an OT Type
        ot_type = OTType.query.filter_by(is_active=True).first()
        if not ot_type:
            print("❌ No active OT Type found.")
            return
            
        print(f"Using OT Type: {ot_type.name} (Multiplier: {ot_type.rate_multiplier})")
        
        # 4. Define Test Data
        test_quantity = 2
        test_rate = 50.0  # Custom rate, different from multiplier (usually 1.0 or 1.5)
        expected_amount = 100.0
        test_date = date.today().isoformat()
        
        payload = {
            "ot_date": test_date,
            "ot_type_id": ot_type.id,
            "quantity": test_quantity,
            "rate": test_rate,
            "notes": "Automated Verification Test"
        }
        
        # 5. Make Request
        client = app.test_client()
        response = client.post('/api/ot/request', data=json.dumps(payload), headers=headers)
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.get_data(as_text=True)}")
            return
            
        data = response.get_json()
        print(f"API Response Data: {data}")
        
        # 6. Verify Response Data
        if data['status'] == 'success':
            resp_data = data['data']
            if float(resp_data['amount']) == expected_amount:
                print(f"✅ API Response Amount Correct: {resp_data['amount']}")
            else:
                 print(f"❌ API Response Amount Incorrect. Expected {expected_amount}, Got {resp_data['amount']}")
                 
            # 7. Verify Database
            request_id = resp_data['id']
            ot_req = OTRequest.query.get(request_id)
            
            if ot_req:
                print(f"DB OTRequest Amount: {ot_req.amount}")
                if float(ot_req.amount) == expected_amount:
                     print("✅ Database OTRequest Amount Correct")
                else:
                     print("❌ Database OTRequest Amount Incorrect")
            else:
                print("❌ OTRequest not found in DB")
                
            # Check OT Attendance (harder to link directly without ID, but we can search by created_at or assume latest)
            # Actually, we can fetch by request? No direct link in API response for Attendance ID unless we check logic.
            # But we can query last created OTAttendance for this employee
            
            ot_att = OTAttendance.query.filter_by(employee_id=test_employee.id).order_by(OTAttendance.created_at.desc()).first()
            if ot_att:
                 print(f"DB OTAttendance Rate: {ot_att.rate}, Amount: {ot_att.amount}")
                 if float(ot_att.rate) == test_rate and float(ot_att.amount) == expected_amount:
                      print("✅ Database OTAttendance Rate & Amount Correct")
                 else:
                      print("❌ Database OTAttendance Incorrect")
            
            # Clean up (Optional, but good practice)
            # db.session.delete(ot_req)
            # if ot_att: db.session.delete(ot_att)
            # db.session.commit()
            
        else:
             print("❌ API reported failure")

if __name__ == "__main__":
    verify_ot_api_rate()
