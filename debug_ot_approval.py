#!/usr/bin/env python3
"""
Debug script to test OT Approval mechanism
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import OTApproval, OTRequest, User, Employee, Role
from datetime import datetime

def test_ot_approval():
    """Test OT approval creation and update"""
    print("=" * 60)
    print("OT APPROVAL DEBUG TEST")
    print("=" * 60)
    
    with app.app_context():
        # Check if tables exist
        print("\n1. Checking database schema...")
        try:
            # Try to query OTApproval
            approval_count = OTApproval.query.count()
            print(f"   ✓ OTApproval table exists ({approval_count} records)")
        except Exception as e:
            print(f"   ✗ OTApproval table error: {str(e)}")
            return
        
        # Check HR Manager role
        print("\n2. Checking HR Manager role...")
        hr_manager_role = Role.query.filter_by(name='HR Manager').first()
        if hr_manager_role:
            print(f"   ✓ HR Manager role found (ID: {hr_manager_role.id})")
            # Count HR Managers
            hr_managers = User.query.filter_by(role_id=hr_manager_role.id).all()
            print(f"   ✓ Found {len(hr_managers)} HR Manager(s)")
            for hm in hr_managers:
                print(f"     - {hm.email} (ID: {hm.id})")
        else:
            print("   ✗ HR Manager role NOT found - this will cause approval to fail!")
        
        # Get a pending approval to test
        print("\n3. Looking for pending approvals...")
        pending = OTApproval.query.filter_by(status='pending_manager').first()
        if pending:
            print(f"   ✓ Found pending approval (ID: {pending.id})")
            print(f"     - OT Request: {pending.ot_request_id}")
            print(f"     - Approver: {pending.approver_id}")
            print(f"     - Status: {pending.status}")
            print(f"     - Created: {pending.created_at}")
            
            # Test updating it
            print("\n4. Testing approval update...")
            try:
                pending.status = 'manager_approved'
                pending.comments = 'Test approval'
                # NOTE: We intentionally DO NOT update created_at
                
                if hr_manager_role and hr_managers:
                    print("   - Creating Level 2 approval...")
                    ot_approval_l2 = OTApproval(
                        ot_request_id=pending.ot_request_id,
                        approver_id=hr_managers[0].id,
                        approval_level=2,
                        status='pending_hr',
                        comments='Test level 2 approval'
                    )
                    db.session.add(ot_approval_l2)
                    print("   ✓ L2 approval object created")
                
                # Try commit
                print("   - Attempting database commit...")
                db.session.commit()
                print("   ✓ Commit successful!")
                
                # Verify
                updated = OTApproval.query.get(pending.id)
                print(f"   ✓ Verification: Status now = {updated.status}")
                
            except Exception as e:
                db.session.rollback()
                print(f"   ✗ Commit failed: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("   ✗ No pending approvals found to test")
        
        print("\n" + "=" * 60)
        print("DEBUG TEST COMPLETE")
        print("=" * 60)

if __name__ == '__main__':
    test_ot_approval()