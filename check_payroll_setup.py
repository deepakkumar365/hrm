#!/usr/bin/env python3
"""Diagnostic script to check payroll setup and company/tenant configuration"""

from app import app, db
from models import Organization, Tenant, Company, User
from flask import current_app

def check_payroll_setup():
    """Check if organizations have tenant_id and companies are set up"""
    
    with app.app_context():
        print("\n" + "="*80)
        print("PAYROLL SETUP DIAGNOSTIC")
        print("="*80 + "\n")
        
        # Check organizations
        print("1. ORGANIZATIONS CHECK:")
        print("-" * 80)
        orgs = Organization.query.all()
        
        if not orgs:
            print("❌ No organizations found!")
            return
        
        for org in orgs:
            print(f"\nOrganization: {org.name} (ID: {org.id})")
            print(f"  - Tenant ID: {org.tenant_id if org.tenant_id else '❌ NOT SET'}")
            
            if org.tenant_id:
                # Check if tenant exists
                tenant = Tenant.query.filter_by(id=org.tenant_id).first()
                if tenant:
                    print(f"  - Tenant Name: {tenant.name}")
                    
                    # Check if company exists for this tenant
                    companies = Company.query.filter_by(tenant_id=org.tenant_id).all()
                    if companies:
                        print(f"  - Companies ({len(companies)}):")
                        for company in companies:
                            print(f"    • {company.name} ({company.code})")
                    else:
                        print(f"  - ❌ NO COMPANIES FOUND for this tenant!")
                else:
                    print(f"  - ❌ Tenant with ID {org.tenant_id} not found!")
            
            # Check users
            users = User.query.filter_by(organization_id=org.id).all()
            if users:
                print(f"  - Users ({len(users)}):")
                for user in users:
                    print(f"    • {user.username} ({user.role.name if user.role else 'No role'})")
        
        # Check Tenants
        print("\n\n2. TENANTS CHECK:")
        print("-" * 80)
        tenants = Tenant.query.all()
        
        if not tenants:
            print("❌ No tenants found!")
        else:
            for tenant in tenants:
                companies = Company.query.filter_by(tenant_id=tenant.id).all()
                print(f"\nTenant: {tenant.name} (ID: {tenant.id})")
                print(f"  - Companies: {len(companies)}")
                for company in companies:
                    print(f"    • {company.name}")
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS:")
        print("="*80)
        
        # Check if setup is needed
        needs_setup = False
        for org in orgs:
            if not org.tenant_id:
                print(f"\n⚠️  Organization '{org.name}' has NO tenant_id")
                needs_setup = True
            else:
                companies = Company.query.filter_by(tenant_id=org.tenant_id).all()
                if not companies:
                    print(f"\n⚠️  Organization '{org.name}' has no companies!")
                    needs_setup = True
        
        if not needs_setup:
            print("\n✅ Setup appears to be complete!")
        else:
            print("\nTo fix this issue:")
            print("1. Run: python run_tenant_company_migration.py")
            print("2. Or manually:")
            print("   - Create a Tenant (if doesn't exist)")
            print("   - Link Organization to Tenant (set tenant_id)")
            print("   - Create a Company for that Tenant")
        
        print("\n")

if __name__ == '__main__':
    check_payroll_setup()