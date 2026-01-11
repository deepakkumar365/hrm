
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
USERNAME = "DEVIT057"
PASSWORD = "Welcome@123"

def login(session):
    print(f"Logging in as {USERNAME}...")
    login_url = f"{BASE_URL}/login"
    
    # Get CSRF token if needed (assuming Flask-WTF?)
    # Simple login usually works if no CSRF on login or if we scrape it.
    # Let's try GET first to check for CSRF token
    r = session.get(login_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    if csrf_token:
        data['csrf_token'] = csrf_token['value']
    
    r = session.post(login_url, data=data)
    if r.status_code == 200 and "Dashboard" in r.text:
        print("Login Successful")
        return True
    elif r.status_code == 302:
         # Redirect means success usually
         print("Login Redirected (Success?)")
         return True
    else:
        print(f"Login Failed. Status: {r.status_code}")
        soup = BeautifulSoup(r.text, 'html.parser')
        # Print alerts/flash messages
        alerts = soup.find_all('div', class_='alert')
        if alerts:
            for alert in alerts:
                print(f"Alert: {alert.text.strip()}")
        else:
            print("No alerts found on page.")
            # Maybe print title or heading to see where we are
            print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
        return False


def approve_ot(session):
    print("Fetching Pending Approvals...")
    approval_url = f"{BASE_URL}/ot/approval"
    r = session.get(approval_url)
    
    if "No Pending Requests" in r.text or "approval-card" not in r.text:
        print("No pending requests found for this user.")
        # Check manager approval?
        check_manager_approval(session)
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    approvals = soup.find_all('div', class_='approval-card')
    print(f"Found {len(approvals)} pending approvals.")
    
    for card in approvals:
        card_id = card.get('id').replace('card_', '')
        print(f"Attempting to approve OT Request ID: {card_id}")
        
        # Approve Action
        # The form posts to /ot/approval
        
        # We need to construct payload from the form
        # But for test, we just send action=approve and required fields
        data = {
            'ot_request_id': card_id, # Wait, the card ID usually maps to approval ID or Request ID?
            # Template says: input name="ot_request_id" value="{{ approval.ot_request.id }}"
            # But the loop is over 'approval'. ID 'card_{{ approval.id }}'.
            # Inside form: input name="ot_request_id" value="{{ approval.ot_request.id }}"
            'action': 'approve',
            'comments': 'Verified by Script'
        }
        
        # We need to extract the actual OT Request ID from the form inside the card
        hidden_input = card.find('input', {'name': 'ot_request_id'})
        if hidden_input:
             data['ot_request_id'] = hidden_input['value']
        else:
             print("Could not find ot_request_id hidden input")
             continue
             
        # Find action hidden field setup?
        # The JS sets 'action' hidden field.
        
        # Send POST
        r = session.post(approval_url, data=data)
        if r.status_code == 200:
            if "OT Final Approved" in r.text:
                print(f"SUCCESS: Approved Request {data['ot_request_id']}")
            else:
                print(f"RESPONSE: {r.text[:200]}...") # Check for flash messages
        else:
            print(f"FAILED: Status {r.status_code}")

def check_manager_approval(session):
    print("Checking Manager Approvals (L1)...")
    url = f"{BASE_URL}/ot/manager-approval"
    r = session.get(url)
    if "No Pending Requests" in r.text:
        print("No L1 pending requests.")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    # Logic for manager approval is different (Bulk action or single?)
    # Let's just report existence
    print("Found L1 pending requests.")

if __name__ == "__main__":
    s = requests.Session()
    if login(s):
        approve_ot(s)
