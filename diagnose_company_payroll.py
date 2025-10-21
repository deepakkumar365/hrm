#!/usr/bin/env python
"""Diagnostic script to debug company selection issue in payroll"""

from app import app, db
from models import User, Organization, Tenant, Company
from flask_login import current_user

def diagnose_payroll_companies():
    """Check the setup for payroll company selection"""
    
    with app.app_context():
        print("\n" + "="*80)
        print("PAYROLL COMPANY SELECTION DIAGNOSIS")
        print("="*80 + "\n")
        
        # Check all users
        users = User.query.all()
        print(f"Total users in system: {len(users)}\n")
        
        for user in users:
            print(f"\n--- User: {user.username} ---")
            print(f"    User ID: {user.id}")
            print(f"    Organization ID: {user.organization_id}")
            
            if user.organization:
                org = user.organization
                print(f"    Organization Name: {org.name}")
                print(f"    Organization Tenant ID: {org.tenant_id}")
                
                if org.tenant_id:
                    # Check if tenant exists
                    tenant = Tenant.query.filter_by(id=org.tenant_id).first()
                    if tenant:
                        print(f"    Tenant Name: {tenant.name}")
                        print(f"    Tenant Code: {tenant.code}")
                        
                        # Check companies for this tenant
                        companies = Company.query.filter_by(
                            tenant_id=org.tenant_id, 
                            is_active=True
                        ).all()
                        print(f"    Companies in tenant: {len(companies)}")
                        
                        if companies:
                            for company in companies:
                                print(f"      - {company.name} (ID: {company.id}, Code: {company.code})")
                        else:
                            print(f"    ⚠️  WARNING: No active companies found for tenant {org.tenant_id}")
                    else:
                        print(f"    ⚠️  ERROR: Tenant {org.tenant_id} not found!")
                else:
                    print(f"    ⚠️  ERROR: Organization has NO tenant_id set!")
            else:
                print(f"    ⚠️  ERROR: User has NO organization!")
        
        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        total_tenants = Tenant.query.count()
        total_companies = Company.query.count()
        total_orgs = Organization.query.count()
        orgs_with_tenant = Organization.query.filter(Organization.tenant_id != None).count()
        
        print(f"Total Tenants: {total_tenants}")
        print(f"Total Companies: {total_companies}")
        print(f"Total Organizations: {total_orgs}")
        print(f"Organizations with Tenant: {orgs_with_tenant}")
        print(f"Organizations without Tenant: {total_orgs - orgs_with_tenant}")
        
        if total_tenants > 0:
            print("\n--- Tenant Details ---")
            tenants = Tenant.query.all()
            for tenant in tenants:
                companies_count = Company.query.filter_by(tenant_id=tenant.id).count()
                print(f"  Tenant: {tenant.name}")
                print(f"    Code: {tenant.code}")
                print(f"    Companies: {companies_count}")
        
        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    diagnose_payroll_companies()