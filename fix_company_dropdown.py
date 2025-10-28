#!/usr/bin/env python
"""
Fix script to ensure company dropdown works in payroll generate page.
This script:
1. Checks current database state
2. Creates missing Tenant if needed
3. Links Organizations to Tenant
4. Creates test Company if needed
5. Assigns employees to Company
"""

import sys
import os
from uuid import uuid4

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    from app import app, db
    from models import User, Organization, Tenant, Company, Employee
    
    with app.app_context():
        print("\n" + "="*80)
        print("COMPANY DROPDOWN FIX SCRIPT")
        print("="*80 + "\n")
        
        try:
            # Step 1: Check existing users and their setup
            print("📋 STEP 1: Checking current users...")
            users = User.query.all()
            print(f"   Found {len(users)} users\n")
            
            if not users:
                print("   ❌ ERROR: No users found in database!")
                print("   Please create users first using the register/create user functions.\n")
                return
            
            # Step 2: Check/Create Tenant
            print("📋 STEP 2: Checking Tenant...")
            tenant = Tenant.query.first()
            
            if not tenant:
                print("   ❌ No tenant found. Creating default tenant...")
                tenant = Tenant(
                    id=uuid4(),
                    name="Default Tenant",
                    code="DEFAULT",
                    description="Default tenant for HRMS",
                    is_active=True
                )
                db.session.add(tenant)
                db.session.commit()
                print(f"   ✅ Created tenant: {tenant.name} (Code: {tenant.code})\n")
            else:
                print(f"   ✅ Tenant found: {tenant.name} (Code: {tenant.code})\n")
            
            # Step 3: Link Organizations to Tenant
            print("📋 STEP 3: Linking Organizations to Tenant...")
            orgs = Organization.query.all()
            print(f"   Found {len(orgs)} organizations")
            
            linked_count = 0
            for org in orgs:
                if not org.tenant_id:
                    org.tenant_id = tenant.id
                    linked_count += 1
                    print(f"   ✅ Linked organization: {org.name}")
            
            if linked_count > 0:
                db.session.commit()
                print(f"   Linked {linked_count} organization(s) to tenant\n")
            else:
                print(f"   ✅ All organizations already linked to tenant\n")
            
            # Step 4: Check/Create Company
            print("📋 STEP 4: Checking Company...")
            company = Company.query.filter_by(tenant_id=tenant.id).first()
            
            if not company:
                print("   ❌ No company found. Creating default company...")
                company = Company(
                    id=uuid4(),
                    tenant_id=tenant.id,
                    name="Default Company",
                    code="DEFAULT-CO",
                    description="Default company for payroll",
                    uen="00000000",
                    is_active=True
                )
                db.session.add(company)
                db.session.commit()
                print(f"   ✅ Created company: {company.name} (Code: {company.code})\n")
            else:
                print(f"   ✅ Company found: {company.name} (Code: {company.code})\n")
            
            # Step 5: Assign employees to company
            print("📋 STEP 5: Assigning employees to company...")
            employees = Employee.query.all()
            print(f"   Found {len(employees)} employees")
            
            assigned_count = 0
            for emp in employees:
                if not emp.company_id:
                    emp.company_id = company.id
                    assigned_count += 1
            
            if assigned_count > 0:
                db.session.commit()
                print(f"   ✅ Assigned {assigned_count} employee(s) to company\n")
            else:
                print(f"   ✅ All employees already assigned to company\n")
            
            # Step 6: Final verification
            print("📋 STEP 6: Final Verification...")
            print("\n   --- User Details ---")
            for user in users:
                print(f"\n   User: {user.username}")
                if user.organization:
                    print(f"     Organization: {user.organization.name}")
                    print(f"     Tenant ID: {user.organization.tenant_id}")
                    
                    if user.organization.tenant_id:
                        companies = Company.query.filter_by(
                            tenant_id=user.organization.tenant_id,
                            is_active=True
                        ).all()
                        print(f"     Companies available: {len(companies)}")
                        for co in companies:
                            print(f"       - {co.name}")
                        
                        if len(companies) == 0:
                            print("       ❌ NO COMPANIES AVAILABLE!")
                        else:
                            print("       ✅ Companies will appear in dropdown!")
                    else:
                        print("       ❌ Organization has NO tenant_id!")
                else:
                    print(f"     ❌ User has NO organization!")
            
            print("\n" + "="*80)
            print("✅ FIX SCRIPT COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("\n📝 Next steps:")
            print("   1. Log in to the application")
            print("   2. Navigate to Payroll > Generate Payroll")
            print("   3. The company dropdown should now show available companies")
            print("\nIf the dropdown is still empty:")
            print("   - Make sure you're logged in as a user with the correct role")
            print("   - Check that employees are created and assigned to the company")
            print("\n")
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR: {str(e)}")
            print(f"\nTraceback:\n{traceback.format_exc()}")
            return False
        
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)