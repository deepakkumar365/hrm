#!/usr/bin/env python
"""
Fix: Create missing EmployeeDocument records for finalized payslips
This handles payslips that were generated before the document-linking fix.

Usage: python fix_payslip_documents.py
"""

import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Payroll, EmployeeDocument

def fix_payslip_documents():
    """Create missing EmployeeDocument records for all approved/finalized payslips"""
    
    with app.app_context():
        print("🔍 Scanning for approved/finalized payslips without document records...")
        
        # Find all approved and finalized payslips
        payrolls = Payroll.query.filter(Payroll.status.in_(['Approved', 'Finalized'])).all()
        print(f"   Found {len(payrolls)} approved/finalized payroll records")
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for payroll in payrolls:
            try:
                # Check if document already exists
                existing_doc = EmployeeDocument.query.filter_by(
                    employee_id=payroll.employee_id,
                    document_type='Salary Slip',
                    month=payroll.pay_period_start.month,
                    year=payroll.pay_period_start.year
                ).first()
                
                if existing_doc:
                    skipped_count += 1
                    continue
                
                # Create new document record
                salary_slip_doc = EmployeeDocument(
                    employee_id=payroll.employee_id,
                    document_type='Salary Slip',
                    file_path=f'payroll/{payroll.id}',  # Virtual path for payroll view
                    issue_date=datetime.now(),
                    month=payroll.pay_period_start.month,
                    year=payroll.pay_period_start.year,
                    description=f"Salary Slip for {payroll.pay_period_start.strftime('%B %Y')}",
                    uploaded_by=None  # System created
                )
                
                db.session.add(salary_slip_doc)
                db.session.commit()
                
                emp = payroll.employee
                print(f"   ✅ Created document for {emp.first_name} {emp.last_name} ({payroll.pay_period_start.strftime('%b %Y')})")
                created_count += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ Error for payroll ID {payroll.id}: {str(e)}")
                error_count += 1
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   ✅ Created: {created_count} documents")
        print(f"   ⏭️  Skipped: {skipped_count} (already have documents)")
        print(f"   ❌ Errors: {error_count}")
        print(f"\n✨ Fix complete! Payslips now visible in Documents menu.")


if __name__ == '__main__':
    fix_payslip_documents()