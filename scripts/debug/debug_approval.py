from app import app
from models import db, OTApproval, OTRequest, User

with app.app_context():
    # Get the pending approval
    approval = OTApproval.query.filter(
        OTApproval.approval_level == 2, 
        OTApproval.status == 'pending_hr'
    ).first()
    
    if approval:
        print(f'Approval ID: {approval.id}')
        print(f'Status: {approval.status}')
        print(f'OT Request ID: {approval.ot_request_id}')
        print(f'Approver ID: {approval.approver_id}')
        
        req = approval.ot_request
        if req:
            print(f'\nOT Request exists: Yes')
            emp_name = req.employee.first_name if req.employee else 'NO EMPLOYEE'
            print(f'  Employee: {emp_name}')
            print(f'  Company: {req.company_id}')
            print(f'  Status: {req.status}')
            print(f'  Requested Hours: {req.requested_hours}')
            
            # Check daily summary
            if req.ot_daily_summary:
                print(f'  OT Daily Summary: YES')
            else:
                print(f'  OT Daily Summary: NO')
        else:
            print(f'OT Request exists: NO')
    else:
        print('No pending HR approvals found')