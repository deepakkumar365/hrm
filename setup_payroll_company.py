#!/usr/bin/env python3
"""
Quick setup script to configure Tenant/Company for Payroll
This links your Organization to a Tenant and creates a Company
"""

import sys
from app import app, db
from models import Organization, Tenant, Company
from uuid import uuid4

def setup_payroll():
    """Setup payroll by creating tenant and company if needed"""
    
    with app.app_context():
        print("\n" + "="*80)
        print("PAYROLL COMPANY SETUP")
        print("="*80 + "\n")
        
        # Get the first organization
        org = Organization.query.first()
        
        if not org:
            print("❌ Error: No organization found in the system!")
            print("Please create an organization first.")
            sys.exit(1)
        
        print(f"Organization: {org.name}")
        
        # Check if organization already has a tenant
        if org.tenant_id:
            print(f"✅ Organization already linked to Tenant ID: {org.tenant_id}")
            tenant = Tenant.query.filter_by(id=org.tenant_id).first()
            if not tenant:
                print(f"❌ ERROR: Tenant {org.tenant_id} not found!")
                sys.exit(1)
            print(f"   Tenant Name: {tenant.name}")
        else:
            print(f"⚠️  Organization NOT linked to any Tenant")
            print("   Creating new Tenant...")
            
            # Create a new tenant
            tenant_id = uuid4()
            tenant_code = org.name[:10].upper().replace(" ", "")
            tenant = Tenant(
                id=tenant_id,
                name=f"{org.name} Tenant",
                code=tenant_code,
                is_active=True,
                created_by='system'
            )
            
            db.session.add(tenant)
            db.session.commit()
            
            # Link organization to tenant
            org.tenant_id = tenant_id
            db.session.commit()
            
            print(f"✅ Tenant created: {tenant.name}")
            print(f"✅ Organization linked to Tenant: {tenant_id}")
        
        # Check if company exists for this tenant
        company = Company.query.filter_by(tenant_id=org.tenant_id).first()
        
        if company:
            print(f"✅ Company already exists: {company.name}")
        else:
            print(f"⚠️  No Company found for this Tenant")
            print("   Creating new Company...")
            
            # Create a new company
            company = Company(
                id=uuid4(),
                tenant_id=org.tenant_id,
                name=f"{org.name}",
                code=org.name[:10].upper().replace(" ", ""),
                is_active=True,
                created_by='system'
            )
            
            db.session.add(company)
            db.session.commit()
            
            print(f"✅ Company created: {company.name} ({company.code})")
        
        print("\n" + "="*80)
        print("✅ SETUP COMPLETE!")
        print("="*80)
        print("\nYou can now use the Payroll > Generate page!")
        print("Try clicking 'Load Employee Data' again.\n")

if __name__ == '__main__':
    setup_payroll()