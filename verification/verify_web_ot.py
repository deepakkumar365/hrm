
# Reuse the same setup as verify_ot_api.py but target the internal API used by the Web UI
# The endpoint is /api/ot/log-entry instead of /api/ot/request
# It uses the same authentication mechanism (login_required, session based usually, but we can fake session or use token if supported, 
# checked routes_api.py - log_ot_entry is @login_required which usually means session. 
# However, routes_api.py has MOBILE_API_GUIDE claiming token support for everything in /api. 
# Let's check routes_ot.py again. It uses @login_required.
# If @login_required is from flask_login, it checks session. 
# But the mobile guide says we can use token. 
# Let's see if we can use the same token auth for this endpoint.
# The endpoint `log_ot_entry` is in `routes_ot.py`.
# `routes_ot.py` uses `@login_required` from `flask_login`.
# This might mean it ONLY works with session cookies unless we have a token loader.
# But `routes_api.py` has `token_required` decorator. `log_ot_entry` uses `@login_required`.
# This means `log_ot_entry` requires a SESSION cookie, not a Bearer token.
# To verify this script-wise, we need to login first to get a session.

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import User, Employee, OTAttendance, OTType
# Import routes to register endpoints
from routes import routes_ot
# Import auth to register user_loader
from core import auth
import json
from datetime import date

def verify_web_ot_api_rate():
    with app.app_context():
        print("--- Verifying Web OT API (Log & Go) Rate Logic ---")
        
        # 1. Find a suitable test user (Employee with a Manager)
        test_employee = None
        users = User.query.all()
        
        user = None
        for u in users:
            if u.employee_profile:
                user = u
                break
        
        if not user:
            print("❌ No suitable test user found (needs employee profile).")
            return
            
        print(f"Testing with User: {user.username} (ID: {user.id})")
        
        # 2. Find Employee Profile
        if not user.employee_profile:
            print("❌ User has no employee profile.")
            return
            
        employee = user.employee_profile
        
        # 3. Find OT Type
        ot_type = OTType.query.filter_by(is_active=True).first()
        if not ot_type:
            print("❌ No active OT Type found.")
            return

        print(f"Using OT Type: {ot_type.name} (Multiplier: {ot_type.rate_multiplier})")

        # 4. Login to get Session (Mocking Flask-Login session)
        client = app.test_client()
        with client:
             with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

             # 5. Define Test Data
             test_quantity = 3
             test_rate = 20.0  
             expected_amount = 60.0
             test_date = date.today().isoformat()
        
             payload = {
                "ot_date": test_date,
                "ot_type_id": ot_type.id,
                "quantity": test_quantity,
                "rate": test_rate, 
                "notes": "Web Verification Test"
             }
        
             # 6. Make Request to /api/ot/log-entry
             response = client.post('/api/ot/log-entry', 
                                 data=json.dumps(payload), 
                                 content_type='application/json')
        
             print(f"Response Status: {response.status_code}")
        
             if response.status_code != 200:
                print(f"❌ Request failed: {response.get_data(as_text=True)}")
                return
            
             data = response.get_json()
             print(f"Response Data: {data}")
        
             if data['success']:
                entry = data['entry']
                print(f"Entry Amount: {entry['amount']}")
            
                if float(entry['amount']) == expected_amount:
                     print(f"✅ Web API Response Amount Correct: {entry['amount']}")
                else:
                     print(f"❌ Web API Response Amount Incorrect. Expected {expected_amount}, Got {entry['amount']}")
                 
                # DB Check
                ot_att = OTAttendance.query.get(entry['id'])
                if ot_att:
                    print(f"DB Rate: {ot_att.rate}, Amount: {ot_att.amount}")
                    if float(ot_att.rate) == test_rate and float(ot_att.amount) == expected_amount:
                        print("✅ Database Correct")
                    else:
                        print("❌ Database Incorrect")
             else:
                print("❌ API reported failure")

if __name__ == "__main__":
    verify_web_ot_api_rate()
