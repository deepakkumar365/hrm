
from app import app
from core.models import User, OTRequest, OTApproval, OTDailySummary, db

def dry_run_approval():
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for test client ease
    
    with app.test_client() as client:
        # Force Login via Session
        with app.app_context():
            u = User.query.filter_by(username='DEVIT057').first()
            if not u:
                print("User DEVIT057 not found in DB.")
                return
            user_id = str(u.id)
            
        with client.session_transaction() as sess:
            sess['_user_id'] = user_id
            sess['_fresh'] = True

        print(f"Forced Login as DEVIT057 (ID: {user_id}).")


        with app.app_context():
            # Find a pending HR approval for this scenario
            # We look for ANY pending HR approval to test the logic
            # Or specifically one associated with this user if needed?
            # HR Manager can see All (or accessible)
            
            pending = OTApproval.query.filter_by(approval_level=2, status='pending_hr').first()
            if not pending:
                print("No Pending HR Approvals found in DB to test.")
                return
            
            ot_req = pending.ot_request
            print(f"Found Pending Approval ID: {pending.id} for Request {ot_req.id} (Emp: {ot_req.employee_id}, Date: {ot_req.ot_date})")

            # Simulate Approval POST
            print("Simulating Approval...")
            resp = client.post('/ot/approval', data={
                'ot_request_id': ot_req.id,
                'action': 'approve',
                'comments': 'Test Approval via Script',
                # dummy allowances
                'kd_and_claim': 10
            }, follow_redirects=True)
            
            if b"OT Final Approved" in resp.data:
                print("SUCCESS: Approval Processed without Error.")
                
                # Verify Summary Created
                summary = OTDailySummary.query.filter_by(ot_request_id=ot_req.id).first()
                if summary:
                    print(f"VERIFIED: OTDailySummary created ID: {summary.id}, Hours: {summary.ot_hours}, Amount: {summary.ot_amount}")
                else:
                    print("FAILURE: OTDailySummary NOT found.")
            else:
                print("FAILURE: Approval did not return success message.")
                # print(resp.data.decode('utf-8'))
                # Find flash
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.data, 'html.parser')
                alerts = soup.find_all('div', class_='alert')
                for a in alerts:
                    print(f"Alert: {a.text.strip()}")

if __name__ == "__main__":
    dry_run_approval()
