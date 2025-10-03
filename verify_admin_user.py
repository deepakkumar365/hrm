"""
Script to verify the admin user was created correctly
"""

from app import app, db
from models import User, Role, Organization

def verify_admin_user():
    with app.app_context():
        try:
            # Find the user
            user = User.query.filter_by(username='admin@noltrion.com').first()
            
            if not user:
                print("❌ User not found!")
                return False
            
            print("\n" + "="*60)
            print("📋 ADMIN USER DETAILS")
            print("="*60)
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Role: {user.role.name if user.role else 'No role'}")
            print(f"Role ID: {user.role_id}")
            print(f"Organization: {user.organization.name if user.organization else 'No organization'}")
            print(f"Organization ID: {user.organization_id}")
            print(f"Active: {user.is_active}")
            print(f"Must Reset Password: {user.must_reset_password}")
            print(f"Created At: {user.created_at}")
            print("="*60)
            
            # Test password
            print("\n🔐 Testing password...")
            if user.check_password('Admin@123'):
                print("✅ Password 'Admin@123' is correct!")
            else:
                print("❌ Password verification failed!")
            
            # Check role permissions
            print("\n🔑 Role Information:")
            if user.role:
                print(f"   Role Name: {user.role.name}")
                print(f"   Role Description: {user.role.description}")
                
                # Check if this is an admin role
                if user.role.name in ['Admin', 'Super Admin']:
                    print("   ✅ This is an ADMIN role with full access!")
                else:
                    print("   ⚠️  This is NOT an admin role!")
            
            # List all available roles
            print("\n📋 All Available Roles:")
            all_roles = Role.query.all()
            for role in all_roles:
                print(f"   - {role.name} (ID: {role.id}): {role.description}")
            
            # List all organizations
            print("\n🏢 All Available Organizations:")
            all_orgs = Organization.query.all()
            for org in all_orgs:
                print(f"   - {org.name} (ID: {org.id})")
            
            print("\n✅ Verification complete!")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    verify_admin_user()