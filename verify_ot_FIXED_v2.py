
import logging
logging.basicConfig(level=logging.ERROR) # Suppress INFO logs

from app import app
from routes import routes # Register general routes & Login Manager
from routes import routes_ot # Register OT routes
from core.models import User, OTRequest, OTApproval, OTDailySummary, db
import sys


def dry_run_approval():
    app.config['WTF_CSRF_ENABLED'] = False
    app.testing = True # Propagate exceptions
    
    print("STARTING VERIFICATION SCRIPT...", flush=True)
    
    # Debug: Check if ot_approval is in url_map
    found = False
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'ot_approval':
            found = True
            break
    if not found:
        print("CRITICAL: 'ot_approval' endpoint NOT found in URL Map!", flush=True)
        # print(app.url_map)
    else:
        print("'ot_approval' endpoint FOUND.", flush=True)



    with app.test_client() as client:
        # Force Login via Session
        with app.app_context():
            u = User.query.filter_by(username='DEVIT057').first()
            if not u:
                print("User DEVIT057 not found in DB.", flush=True)
                return
            user_id = str(u.id)
            department = u.employee_profile.department if u.employee_profile else "None"
            print(f"User Found: {u.username} (ID: {u.id}), Dept: {department}, Role: {u.role.name}", flush=True)
            
            # Find a pending HR approval to test on
            # We want one that this user CAN approve.
            # HR Manager can generally approve all (unless restricted by company/tenant)
            
            query = OTApproval.query.filter_by(approval_level=2, status='pending_hr')
            pending_approvals = query.all()
            print(f"Found {len(pending_approvals)} total pending HR approvals in DB.", flush=True)
            
            target_approval = None
            if pending_approvals:
                 target_approval = pending_approvals[0]
            
            if not target_approval:
                print("No Pending HR Approvals found to test. Cannot verify Approval Logic.", flush=True)
                return

            ot_req = target_approval.ot_request
            print(f"Targeting Approval ID: {target_approval.id} for Request {ot_req.id} (Emp: {ot_req.employee_id}, Date: {ot_req.ot_date})", flush=True)
            
        with client.session_transaction() as sess:
            sess['_user_id'] = user_id
            sess['_fresh'] = True

        print(f"Forced Login as DEVIT057.", flush=True)
        
        # Simulate Approval POST
        print("Simulating Approval Request...", flush=True)
        resp = client.post('/ot/approval', data={
            'ot_request_id': ot_req.id,
            'action': 'approve',
            'comments': 'Test Approval via VS Code Script',
            'kd_and_claim': 10
        }, follow_redirects=True)
        
        if b"OT Final Approved" in resp.data:
            print("SUCCESS: Approval Processed without Error.", flush=True)
            
            # Verify Summary Created
            with app.app_context():
                summary = OTDailySummary.query.filter_by(ot_request_id=ot_req.id).first()
                if summary:
                    print(f"VERIFIED: OTDailySummary created ID: {summary.id}, Hours: {summary.ot_hours}, Amount: {summary.ot_amount}, Status: {summary.status}", flush=True)
                else:
                    print("FAILURE: OTDailySummary NOT found after success message.", flush=True)
        else:
            print("FAILURE: Approval did not return success message.", flush=True)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.data, 'html.parser')
            alerts = soup.find_all('div', class_='alert')
            for a in alerts:
                print(f"Alert: {a.text.strip()}", flush=True)
                
            if not alerts:
                 print("No alerts found.", flush=True)
                 print(f"Page Title: {soup.title.string if soup.title else 'No Title'}", flush=True)
                 print("Page Content Snippet:", flush=True)
                 print(resp.data.decode('utf-8', errors='ignore')[:1000], flush=True)


if __name__ == "__main__":
    dry_run_approval()
