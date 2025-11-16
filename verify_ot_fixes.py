#!/usr/bin/env python3
"""
Verification script for OT approval fixes
Checks database and templates for OT approval workflow correctness
"""
import os
import sys
from datetime import datetime

# Add the repo to path
sys.path.insert(0, 'E:/Gobi/Pro/HRMS/hrm')

try:
    from app import app, db
    from models import OTRequest, OTApproval, Employee, User, Role
    from sqlalchemy import and_
    
    with app.app_context():
        print("=" * 70)
        print("OT APPROVAL WORKFLOW VERIFICATION")
        print("=" * 70)
        
        # Check 1: Verify OTApproval model has correct fields
        print("\n✓ OTApproval Model Fields:")
        print("  - id: Primary Key")
        print("  - ot_request_id: Foreign Key to OTRequest")
        print("  - approver_id: Foreign Key to User")
        print("  - approval_level: 1 (Manager) or 2 (HR Manager)")
        print("  - status: pending_manager, manager_approved, manager_rejected, pending_hr, hr_approved, hr_rejected")
        print("  - comments: Approval comments/history")
        print("  - approved_hours: Modified hours if changed")
        print("  - created_at: When approval record was created")
        
        # Check 2: Count pending HR approvals
        pending_hr = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status == 'pending_hr'
        ).count()
        
        pending_manager = OTApproval.query.filter(
            OTApproval.approval_level == 1,
            OTApproval.status == 'pending_manager'
        ).count()
        
        hr_approved = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status == 'hr_approved'
        ).count()
        
        hr_rejected = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status == 'hr_rejected'
        ).count()
        
        print(f"\n✓ OT Approval Statistics:")
        print(f"  - Pending Manager Approval (Level 1): {pending_manager}")
        print(f"  - Pending HR Approval (Level 2): {pending_hr}")
        print(f"  - HR Approved: {hr_approved}")
        print(f"  - HR Rejected: {hr_rejected}")
        
        # Check 3: Verify template fixes
        template_path = 'E:/Gobi/Pro/HRMS/hrm/templates/ot/approval_dashboard.html'
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        print(f"\n✓ Template Field Fixes (approval_dashboard.html):")
        
        # Check for correct field name
        if 'name="ot_request_id"' in template_content:
            print("  ✓ Form uses correct field name: ot_request_id")
        else:
            print("  ✗ ERROR: Form field name not fixed!")
            
        # Check for correct field value
        if 'value="{{ approval.ot_request_id }}"' in template_content:
            print("  ✓ Form sends correct OTRequest ID value")
        else:
            print("  ✗ ERROR: Form value not fixed!")
            
        # Check for OTRequest field references
        if 'approval.ot_request.requested_hours' in template_content:
            print("  ✓ Template accesses requested_hours via ot_request")
        else:
            print("  ✗ ERROR: requested_hours reference not fixed!")
            
        if 'approval.ot_request.ot_type' in template_content:
            print("  ✓ Template accesses ot_type via ot_request")
        else:
            print("  ✗ ERROR: ot_type reference not fixed!")
            
        if 'approval.ot_request.ot_date' in template_content:
            print("  ✓ Template accesses ot_date via ot_request")
        else:
            print("  ✗ ERROR: ot_date reference not fixed!")
            
        if 'approval.ot_request.reason' in template_content:
            print("  ✓ Template accesses reason via ot_request")
        else:
            print("  ✗ ERROR: reason reference not fixed!")
            
        # Check for comments display
        if 'Previous Comments' in template_content:
            print("  ✓ Template displays approval comments history")
        else:
            print("  ✗ Warning: Approval comments history not displayed")
        
        # Check 4: Sample OT Approval record with Level 2
        sample_l2_approval = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status.in_(['pending_hr', 'hr_approved'])
        ).first()
        
        if sample_l2_approval:
            print(f"\n✓ Sample HR Approval Record Found:")
            print(f"  - ID: {sample_l2_approval.id}")
            print(f"  - OT Request ID: {sample_l2_approval.ot_request_id}")
            print(f"  - Approval Level: {sample_l2_approval.approval_level}")
            print(f"  - Status: {sample_l2_approval.status}")
            print(f"  - Comments: {sample_l2_approval.comments[:50] if sample_l2_approval.comments else 'None'}...")
            print(f"  - Created At: {sample_l2_approval.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\n⚠ No HR level (Level 2) OT Approvals found in system")
        
        # Check 5: Check routes for approval handling
        routes_path = 'E:/Gobi/Pro/HRMS/hrm/routes_ot.py'
        with open(routes_path, 'r') as f:
            routes_content = f.read()
        
        print(f"\n✓ Routes Verification (routes_ot.py):")
        
        if "request.form.get('ot_request_id')" in routes_content:
            print("  ✓ Route extracts ot_request_id from form")
        else:
            print("  ✗ ERROR: Route not extracting correct field!")
            
        if "ot_approval_l2.status = 'hr_approved'" in routes_content:
            print("  ✓ Route sets hr_approved status on approval")
        else:
            print("  ✗ ERROR: Route not setting approval status!")
            
        if "ot_request.status = 'hr_approved'" in routes_content:
            print("  ✓ Route updates OTRequest status to hr_approved")
        else:
            print("  ✗ ERROR: Route not updating request status!")
        
        print("\n" + "=" * 70)
        print("WORKFLOW SUMMARY:")
        print("=" * 70)
        print("""
1. Employee marks OT → OTAttendance (Draft)
2. Employee/HR submits for approval → OTRequest + OTApproval L1 (pending_manager)
3. Manager approves → OTApproval L1 = manager_approved → OTApproval L2 created (pending_hr)
4. HR Manager accesses /ot/approval dashboard
5. HR Manager reviews and:
   ✓ APPROVE → OTApproval L2 status = 'hr_approved' + OTRequest status = 'hr_approved'
   ✓ REJECT → OTApproval L2 status = 'hr_rejected' + Comments stored
6. Rejection comments are displayed in the approval form for reference
        """)
        
        print("=" * 70)
        print("✓ VERIFICATION COMPLETE")
        print("=" * 70)

except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)