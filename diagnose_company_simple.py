#!/usr/bin/env python
"""Simple diagnostic - outputs to file"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import User, Organization, Tenant, Company, Employee
    
    with app.app_context():
        output = []
        output.append("="*80)
        output.append("PAYROLL COMPANY SELECTION DIAGNOSIS")
        output.append("="*80)
        output.append("")
        
        # Check all users
        users = User.query.all()
        output.append(f"Total users in system: {len(users)}")
        output.append("")
        
        for user in users:
            output.append(f"--- User: {user.username} ---")
            output.append(f"    User ID: {user.id}")
            output.append(f"    Organization ID: {user.organization_id}")
            
            if user.organization:
                org = user.organization
                output.append(f"    Organization Name: {org.name}")
                output.append(f"    Organization Tenant ID: {org.tenant_id}")
                
                if org.tenant_id:
                    # Check if tenant exists
                    tenant = Tenant.query.filter_by(id=org.tenant_id).first()
                    if tenant:
                        output.append(f"    Tenant Name: {tenant.name}")
                        output.append(f"    Tenant Code: {tenant.code}")
                        
                        # Check companies for this tenant
                        companies = Company.query.filter_by(
                            tenant_id=org.tenant_id, 
                            is_active=True
                        ).all()
                        output.append(f"    Companies in tenant: {len(companies)}")
                        
                        if companies:
                            for company in companies:
                                output.append(f"      - {company.name} (ID: {company.id})")
                        else:
                            output.append(f"    ⚠️  NO ACTIVE COMPANIES FOUND for tenant {org.tenant_id}")
                    else:
                        output.append(f"    ❌ Tenant {org.tenant_id} not found!")
                else:
                    output.append(f"    ❌ Organization has NO tenant_id set!")
            else:
                output.append(f"    ❌ User has NO organization!")
            
            output.append("")
        
        # Summary statistics
        output.append("="*80)
        output.append("SUMMARY STATISTICS")
        output.append("="*80)
        
        total_tenants = Tenant.query.count()
        total_companies = Company.query.count()
        total_orgs = Organization.query.count()
        orgs_with_tenant = Organization.query.filter(Organization.tenant_id != None).count()
        total_employees = Employee.query.count()
        employees_with_company = Employee.query.filter(Employee.company_id != None).count()
        
        output.append(f"Total Tenants: {total_tenants}")
        output.append(f"Total Companies: {total_companies}")
        output.append(f"Total Organizations: {total_orgs}")
        output.append(f"Organizations with Tenant: {orgs_with_tenant}")
        output.append(f"Organizations without Tenant: {total_orgs - orgs_with_tenant}")
        output.append(f"Total Employees: {total_employees}")
        output.append(f"Employees with Company assigned: {employees_with_company}")
        
        if total_tenants > 0:
            output.append("")
            output.append("--- Tenant Details ---")
            tenants = Tenant.query.all()
            for tenant in tenants:
                companies_count = Company.query.filter_by(tenant_id=tenant.id).count()
                output.append(f"  Tenant: {tenant.name} (Code: {tenant.code})")
                output.append(f"    Companies: {companies_count}")
        
        output.append("")
        output.append("="*80)
        
        # Write to file
        with open("D:/Projects/HRMS/hrm/DIAGNOSIS_OUTPUT.txt", "w") as f:
            f.write("\n".join(output))
        
        print("\n".join(output))
        
except Exception as e:
    import traceback
    error_output = f"ERROR: {str(e)}\n\n{traceback.format_exc()}"
    print(error_output)
    with open("D:/Projects/HRMS/hrm/DIAGNOSIS_ERROR.txt", "w") as f:
        f.write(error_output)