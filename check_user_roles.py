"""
Script to check user roles and diagnose the tenantadmin login issue
"""
from app import app, db
from models import User, Role, Organization, Company, Tenant

def check_user_roles():
    with app.app_context():
        print("\n" + "="*60)
        print("CHECKING USER ROLES AND CONFIGURATION")
        print("="*60)
        
        # Check all roles
        print("\n📋 ALL ROLES IN DATABASE:")
        print("-" * 60)
        roles = Role.query.all()
        for role in roles:
            user_count = User.query.filter_by(role_id=role.id).count()
            print(f"  ID: {role.id} | Name: '{role.name}' | Users: {user_count} | Active: {role.is_active}")
        
        # Check all users
        print("\n👥 ALL USERS IN DATABASE:")
        print("-" * 60)
        users = User.query.all()
        for user in users:
            role_name = user.role.name if user.role else "NO ROLE"
            org_name = user.organization.name if user.organization else "NO ORG"
            tenant_id = user.organization.tenant_id if user.organization else None
            print(f"  Username: '{user.username}'")
            print(f"    - Role: '{role_name}' (ID: {user.role_id})")
            print(f"    - Organization: '{org_name}' (ID: {user.organization_id})")
            print(f"    - Tenant ID: {tenant_id}")
            print(f"    - Active: {user.is_active}")
            print()
        
        # Check tenantadmin specifically
        print("\n🔍 CHECKING 'tenantadmin' USER:")
        print("-" * 60)
        tenantadmin = User.query.filter_by(username='tenantadmin').first()
        if tenantadmin:
            print(f"  ✅ User 'tenantadmin' EXISTS")
            print(f"  - ID: {tenantadmin.id}")
            print(f"  - Email: {tenantadmin.email}")
            print(f"  - Role: '{tenantadmin.role.name if tenantadmin.role else 'NO ROLE'}'")
            print(f"  - Role ID: {tenantadmin.role_id}")
            print(f"  - Organization ID: {tenantadmin.organization_id}")
            
            if tenantadmin.organization:
                print(f"  - Organization Name: '{tenantadmin.organization.name}'")
                print(f"  - Organization Tenant ID: {tenantadmin.organization.tenant_id}")
                
                if tenantadmin.organization.tenant_id:
                    company = Company.query.filter_by(tenant_id=tenantadmin.organization.tenant_id).first()
                    if company:
                        print(f"  - Company: '{company.name}' (ID: {company.id})")
                    else:
                        print(f"  ⚠️  NO COMPANY found for tenant_id: {tenantadmin.organization.tenant_id}")
                else:
                    print(f"  ⚠️  Organization has NO tenant_id assigned")
            else:
                print(f"  ⚠️  NO ORGANIZATION assigned")
            
            print(f"  - Active: {tenantadmin.is_active}")
            
            # Test password
            test_password = 'tenantadmin123'
            password_valid = tenantadmin.check_password(test_password)
            print(f"  - Password '{test_password}' valid: {password_valid}")
        else:
            print(f"  ❌ User 'tenantadmin' DOES NOT EXIST")
        
        # Check organizations and tenants
        print("\n🏢 ORGANIZATIONS:")
        print("-" * 60)
        orgs = Organization.query.all()
        for org in orgs:
            print(f"  ID: {org.id} | Name: '{org.name}' | Tenant ID: {org.tenant_id}")
        
        print("\n🏛️  TENANTS:")
        print("-" * 60)
        tenants = Tenant.query.all()
        for tenant in tenants:
            company_count = Company.query.filter_by(tenant_id=tenant.id).count()
            print(f"  ID: {tenant.id} | Name: '{tenant.name}' | Code: '{tenant.code}' | Companies: {company_count}")
        
        print("\n🏭 COMPANIES:")
        print("-" * 60)
        companies = Company.query.all()
        for company in companies:
            print(f"  ID: {company.id} | Name: '{company.name}' | Tenant ID: {company.tenant_id}")
        
        print("\n" + "="*60)
        print("DIAGNOSIS COMPLETE")
        print("="*60 + "\n")

if __name__ == '__main__':
    check_user_roles()