"""
Direct script to create tenantadmin user with proper setup
Run with: python create_tenantadmin.py
"""

from app import app, db
from models import User, Role, Organization, Company, Tenant
from sqlalchemy import text

def create_tenantadmin():
    with app.app_context():
        print("\n" + "="*70)
        print("CREATING/FIXING TENANTADMIN USER")
        print("="*70 + "\n")
        
        try:
            # Step 1: Get or create ADMIN role
            print("Step 1: Checking ADMIN role...")
            admin_role = Role.query.filter_by(name='ADMIN').first()
            if not admin_role:
                print("   Creating ADMIN role...")
                admin_role = Role(name='ADMIN', description='Administrator role', is_active=True)
                db.session.add(admin_role)
                db.session.flush()
                print(f"   ✅ Created ADMIN role (ID: {admin_role.id})")
            else:
                print(f"   ✅ ADMIN role exists (ID: {admin_role.id})")
            
            # Step 2: Get or create Tenant
            print("\nStep 2: Checking Tenant...")
            tenant = Tenant.query.first()
            if not tenant:
                print("   Creating Demo Tenant...")
                tenant = Tenant(
                    name='Demo Tenant',
                    code='DEMO',
                    description='Demo tenant for testing',
                    is_active=True,
                    country_code='SG',
                    currency_code='SGD',
                    created_by='system'
                )
                db.session.add(tenant)
                db.session.flush()
                print(f"   ✅ Created tenant (ID: {tenant.id})")
            else:
                print(f"   ✅ Tenant exists: {tenant.name} (ID: {tenant.id})")
            
            # Step 3: Get or create Organization
            print("\nStep 3: Checking Organization...")
            org = Organization.query.filter_by(tenant_id=tenant.id).first()
            if not org:
                print("   Creating organization for tenant...")
                org = Organization(
                    name='Demo Organization',
                    tenant_id=tenant.id
                )
                db.session.add(org)
                db.session.flush()
                print(f"   ✅ Created organization (ID: {org.id})")
            else:
                print(f"   ✅ Organization exists: {org.name} (ID: {org.id})")
            
            # Step 4: Get or create Company
            print("\nStep 4: Checking Company...")
            company = Company.query.filter_by(tenant_id=tenant.id).first()
            if not company:
                print("   Creating company for tenant...")
                company = Company(
                    name='Demo Company',
                    tenant_id=tenant.id,
                    registration_number='DEMO001',
                    is_active=True
                )
                db.session.add(company)
                db.session.flush()
                print(f"   ✅ Created company (ID: {company.id})")
            else:
                print(f"   ✅ Company exists: {company.name} (ID: {company.id})")
            
            # Step 5: Check/create tenantadmin user
            print("\nStep 5: Checking tenantadmin user...")
            tenantadmin = User.query.filter_by(username='tenantadmin').first()
            
            if tenantadmin:
                print(f"   User 'tenantadmin' exists (ID: {tenantadmin.id})")
                print("   Updating configuration...")
                
                # Update role if needed
                if tenantadmin.role_id != admin_role.id:
                    print(f"   - Updating role from '{tenantadmin.role.name if tenantadmin.role else 'None'}' to 'ADMIN'")
                    tenantadmin.role_id = admin_role.id
                
                # Update organization if needed
                if tenantadmin.organization_id != org.id:
                    print(f"   - Updating organization to '{org.name}'")
                    tenantadmin.organization_id = org.id
                
                # Ensure active
                if not tenantadmin.is_active:
                    print("   - Activating user")
                    tenantadmin.is_active = True
                
                # Reset password to known value
                print("   - Resetting password to 'tenantadmin123'")
                tenantadmin.set_password('tenantadmin123')
                tenantadmin.must_reset_password = False
                
                print("   ✅ Updated tenantadmin user")
            else:
                print("   Creating new tenantadmin user...")
                tenantadmin = User(
                    username='tenantadmin',
                    email='tenantadmin@hrm.com',
                    first_name='Tenant',
                    last_name='Admin',
                    organization_id=org.id,
                    role_id=admin_role.id,
                    is_active=True,
                    must_reset_password=False
                )
                tenantadmin.set_password('tenantadmin123')
                db.session.add(tenantadmin)
                db.session.flush()
                print(f"   ✅ Created tenantadmin user (ID: {tenantadmin.id})")
            
            # Commit all changes
            db.session.commit()
            
            print("\n" + "="*70)
            print("✅ SUCCESS - TENANTADMIN USER READY")
            print("="*70)
            print("\nLogin Credentials:")
            print("   Username: tenantadmin")
            print("   Password: tenantadmin123")
            print("\nUser Configuration:")
            print(f"   - User ID: {tenantadmin.id}")
            print(f"   - Role: {tenantadmin.role.name} (ID: {tenantadmin.role_id})")
            print(f"   - Organization: {tenantadmin.organization.name} (ID: {tenantadmin.organization_id})")
            print(f"   - Tenant ID: {tenantadmin.organization.tenant_id}")
            print(f"   - Company: {company.name} (ID: {company.id})")
            print(f"   - Active: {tenantadmin.is_active}")
            print("\n" + "="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            print("\nRolling back changes...")
            return False
        
        return True

if __name__ == '__main__':
    success = create_tenantadmin()
    if success:
        print("You can now login with username 'tenantadmin' and password 'tenantadmin123'")
    else:
        print("Failed to create tenantadmin user. Check the error messages above.")