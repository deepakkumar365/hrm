"""
Script to setup or verify tenantadmin user
Run this with: flask shell < setup_tenantadmin.py
Or manually in flask shell
"""

from app import app, db
from models import User, Role, Organization, Company, Tenant
from werkzeug.security import generate_password_hash
import uuid

def setup_tenantadmin():
    with app.app_context():
        print("\n" + "="*70)
        print("TENANT ADMIN SETUP SCRIPT")
        print("="*70)
        
        # Check if tenantadmin exists
        tenantadmin = User.query.filter_by(username='tenantadmin').first()
        
        if tenantadmin:
            print("\n✅ User 'tenantadmin' already exists")
            print(f"   - ID: {tenantadmin.id}")
            print(f"   - Email: {tenantadmin.email}")
            print(f"   - Role: {tenantadmin.role.name if tenantadmin.role else 'NO ROLE'}")
            print(f"   - Organization ID: {tenantadmin.organization_id}")
            
            if tenantadmin.organization:
                print(f"   - Organization: {tenantadmin.organization.name}")
                print(f"   - Tenant ID: {tenantadmin.organization.tenant_id}")
                
                if tenantadmin.organization.tenant_id:
                    company = Company.query.filter_by(tenant_id=tenantadmin.organization.tenant_id).first()
                    if company:
                        print(f"   - Company: {company.name}")
                    else:
                        print(f"   ⚠️  NO COMPANY for this tenant")
            
            # Check if we need to fix anything
            needs_fix = False
            
            # Check role
            if not tenantadmin.role or tenantadmin.role.name not in ['ADMIN', 'Admin']:
                print(f"\n⚠️  Role issue detected: '{tenantadmin.role.name if tenantadmin.role else 'NO ROLE'}'")
                needs_fix = True
            
            # Check organization
            if not tenantadmin.organization:
                print(f"\n⚠️  No organization assigned")
                needs_fix = True
            elif not tenantadmin.organization.tenant_id:
                print(f"\n⚠️  Organization has no tenant_id")
                needs_fix = True
            elif tenantadmin.organization.tenant_id:
                company = Company.query.filter_by(tenant_id=tenantadmin.organization.tenant_id).first()
                if not company:
                    print(f"\n⚠️  No company for tenant_id: {tenantadmin.organization.tenant_id}")
                    needs_fix = True
            
            if needs_fix:
                print("\n🔧 Would you like to fix these issues? (This script will show you what to do)")
                print("\nTo fix manually:")
                print("1. Ensure ADMIN role exists:")
                print("   admin_role = Role.query.filter_by(name='ADMIN').first()")
                print("   if not admin_role:")
                print("       admin_role = Role(name='ADMIN', description='Admin role')")
                print("       db.session.add(admin_role)")
                print("       db.session.commit()")
                print("\n2. Update user role:")
                print(f"   user = User.query.get({tenantadmin.id})")
                print("   user.role_id = admin_role.id")
                print("   db.session.commit()")
                
                if not tenantadmin.organization or not tenantadmin.organization.tenant_id:
                    print("\n3. Create/assign organization with tenant:")
                    print("   # First, create a tenant if none exists")
                    print("   tenant = Tenant(name='Demo Tenant', code='DEMO', is_active=True)")
                    print("   db.session.add(tenant)")
                    print("   db.session.flush()")
                    print("   # Create organization")
                    print("   org = Organization(name='Demo Organization', tenant_id=tenant.id)")
                    print("   db.session.add(org)")
                    print("   db.session.flush()")
                    print(f"   user = User.query.get({tenantadmin.id})")
                    print("   user.organization_id = org.id")
                    print("   db.session.commit()")
                
                if tenantadmin.organization and tenantadmin.organization.tenant_id:
                    company = Company.query.filter_by(tenant_id=tenantadmin.organization.tenant_id).first()
                    if not company:
                        print("\n4. Create company for tenant:")
                        print(f"   tenant_id = '{tenantadmin.organization.tenant_id}'")
                        print("   company = Company(")
                        print("       name='Demo Company',")
                        print("       tenant_id=tenant_id,")
                        print("       registration_number='DEMO001',")
                        print("       is_active=True")
                        print("   )")
                        print("   db.session.add(company)")
                        print("   db.session.commit()")
        else:
            print("\n❌ User 'tenantadmin' does NOT exist")
            print("\nTo create tenantadmin user, run these commands in flask shell:")
            print("\n# 1. Get or create ADMIN role")
            print("admin_role = Role.query.filter_by(name='ADMIN').first()")
            print("if not admin_role:")
            print("    admin_role = Role(name='ADMIN', description='Admin role')")
            print("    db.session.add(admin_role)")
            print("    db.session.flush()")
            print()
            print("# 2. Get or create tenant")
            print("tenant = Tenant.query.first()")
            print("if not tenant:")
            print("    tenant = Tenant(name='Demo Tenant', code='DEMO', is_active=True)")
            print("    db.session.add(tenant)")
            print("    db.session.flush()")
            print()
            print("# 3. Get or create organization")
            print("org = Organization.query.filter_by(tenant_id=tenant.id).first()")
            print("if not org:")
            print("    org = Organization(name='Demo Organization', tenant_id=tenant.id)")
            print("    db.session.add(org)")
            print("    db.session.flush()")
            print()
            print("# 4. Create tenantadmin user")
            print("from models import User")
            print("tenantadmin = User(")
            print("    username='tenantadmin',")
            print("    email='tenantadmin@hrm.com',")
            print("    first_name='Tenant',")
            print("    last_name='Admin',")
            print("    organization_id=org.id,")
            print("    role_id=admin_role.id,")
            print("    is_active=True,")
            print("    must_reset_password=False")
            print(")")
            print("tenantadmin.set_password('tenantadmin123')")
            print("db.session.add(tenantadmin)")
            print()
            print("# 5. Create company for tenant")
            print("company = Company.query.filter_by(tenant_id=tenant.id).first()")
            print("if not company:")
            print("    company = Company(")
            print("        name='Demo Company',")
            print("        tenant_id=tenant.id,")
            print("        registration_number='DEMO001',")
            print("        is_active=True")
            print("    )")
            print("    db.session.add(company)")
            print()
            print("# 6. Commit all changes")
            print("db.session.commit()")
            print()
            print("print('✅ Tenantadmin user created successfully!')")
        
        print("\n" + "="*70)
        print("CURRENT DATABASE STATE")
        print("="*70)
        
        print("\n📋 ROLES:")
        roles = Role.query.all()
        for role in roles:
            print(f"   - {role.name} (ID: {role.id})")
        
        print("\n🏛️  TENANTS:")
        tenants = Tenant.query.all()
        for tenant in tenants:
            print(f"   - {tenant.name} ({tenant.code}) - ID: {tenant.id}")
        
        print("\n🏢 ORGANIZATIONS:")
        orgs = Organization.query.all()
        for org in orgs:
            print(f"   - {org.name} (ID: {org.id}, Tenant: {org.tenant_id})")
        
        print("\n🏭 COMPANIES:")
        companies = Company.query.all()
        for company in companies:
            print(f"   - {company.name} (ID: {company.id}, Tenant: {company.tenant_id})")
        
        print("\n👥 USERS:")
        users = User.query.all()
        for user in users:
            role_name = user.role.name if user.role else "NO ROLE"
            print(f"   - {user.username} | Role: {role_name} | Org ID: {user.organization_id}")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    setup_tenantadmin()