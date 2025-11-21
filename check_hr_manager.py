from app import app
from models import db, User, OTApproval, OTRequest

with app.app_context():
    # Find HR Manager users
    hr_managers = User.query.filter(
        User.role.has(name='HR Manager')
    ).all()
    
    print(f"Total HR Manager users: {len(hr_managers)}\n")
    
    for user in hr_managers:
        print(f"--- User: {user.username} (ID: {user.id}) ---")
        print(f"  Role: {user.role.name if user.role else 'N/A'}")
        
        # Check if they have employee_profile
        if hasattr(user, 'employee_profile') and user.employee_profile:
            print(f"  Employee Profile: YES")
            print(f"  Company ID: {user.employee_profile.company_id}")
            emp_name = user.employee_profile.first_name if user.employee_profile.first_name else 'Unknown'
            print(f"  Employee Name: {emp_name}")
        else:
            print(f"  Employee Profile: NO")
        
        # Check what approvals they would see
        query = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status.in_(['pending_hr', 'hr_rejected'])
        )
        
        if user.employee_profile and user.employee_profile.company_id:
            query = query.join(OTRequest).filter(OTRequest.company_id == user.employee_profile.company_id)
        
        count = query.count()
        print(f"  Would see {count} pending approvals")
        print()
    
    # Also show what's in the database
    print("\n=== DATABASE CHECK ===")
    print(f"Total OTApproval records (Level 2, pending_hr): ", end="")
    count = OTApproval.query.filter(
        OTApproval.approval_level == 2,
        OTApproval.status == 'pending_hr'
    ).count()
    print(count)
    
    # Show the approval details
    approval = OTApproval.query.filter(
        OTApproval.approval_level == 2,
        OTApproval.status == 'pending_hr'
    ).first()
    
    if approval:
        req = approval.ot_request
        print(f"\nPending Approval Details:")
        print(f"  Approval ID: {approval.id}")
        print(f"  OT Request ID: {approval.ot_request_id}")
        print(f"  OT Request Company ID: {req.company_id}")
        print(f"  Employee: {req.employee.first_name} {req.employee.last_name}")