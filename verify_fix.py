from app import app
from core.models import User, Employee

def verify_fix():
    print("Verifying Fix...")
    # 0. Get Employee ID
    with app.app_context():
        u = User.query.filter_by(username='DEVIT058').first()
        if not u:
            print("User DEVIT058 not found")
            return
        emp_id = u.employee_profile.id
        print(f"Testing for Employee ID: {emp_id}")

    # 1. Call the API using test client
    with app.test_client() as client:
        # Simulate Login (requires patching or disabled auth, assumes @require_role works with test client context if logged in or bypassed)
        # However, require_role usually checks current_user.
        # So we better use a context block to spoof login or just use the logic-check approach if API testing is hard.
        
        # Actually, simpler: Use the `reproduce_issue` approach but IMPORT the function and run it?
        # No, `reproduce_issue.py` checked DB. We want to check the LOGIC of `payroll_preview_api`.
        # Since I cannot easily log in via test client without more setup, I will mock the request context.
        
        with app.test_request_context('/api/payroll/preview', query_string={'month': 1, 'year': 2026, 'employee_id': emp_id}):
             from routes.routes import payroll_preview_api
             from flask_login import login_user
             
             # Need to login a user with correct role
             with app.app_context():
                 admin = User.query.filter(User.role_id.in_([1, 2])).first() # Super Admin or Admin
                 if admin:
                     login_user(admin)
                     print(f"Logged in as {admin.username}")
                     
                     # CALL API
                     response = payroll_preview_api()
                     
                     # Response is a tuple or json, payroll_preview_api returns jsonify so it's a Response object
                     data = response.get_json()
                     
                     if data['success']:
                         for e in data['employees']:
                             if e['id'] == emp_id:
                                 print(f"API Returned: Hours={e['ot_hours']}, Amount={e['ot_amount']}")
                                 if e['ot_amount'] > 0:
                                     print("SUCCESS: OT Amount is updated in preview!")
                                 else:
                                     print("FAILURE: OT Amount is still 0.")
                     else:
                         print(f"API Failed: {data.get('message')}")
                 else:
                     print("No admin user found to run test.")

if __name__ == "__main__":
    verify_fix()
