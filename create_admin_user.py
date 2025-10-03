"""
Script to create an Admin user for Noltrion
Username: admin@noltrion.com
Password: Admin@123
Role: Admin (full access)
"""

from app import app, db
from models import User, Role, Organization

def create_admin_user():
    with app.app_context():
        try:
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == 'admin@noltrion.com') | 
                (User.email == 'admin@noltrion.com')
            ).first()
            
            if existing_user:
                print(f"❌ User already exists with username: {existing_user.username}")
                print(f"   Email: {existing_user.email}")
                print(f"   Role: {existing_user.role.name if existing_user.role else 'No role'}")
                print(f"   Active: {existing_user.is_active}")
                return False
            
            # Get or create Admin role
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                print("⚠️  Admin role not found. Creating Admin role...")
                admin_role = Role(
                    name='Admin',
                    description='Administrator with full system access'
                )
                db.session.add(admin_role)
                db.session.flush()
                print(f"✅ Admin role created with ID: {admin_role.id}")
            else:
                print(f"✅ Found Admin role with ID: {admin_role.id}")
            
            # Get or create default organization
            organization = Organization.query.first()
            if not organization:
                print("⚠️  No organization found. Creating default organization...")
                organization = Organization(name='Noltrion')
                db.session.add(organization)
                db.session.flush()
                print(f"✅ Organization created: {organization.name} (ID: {organization.id})")
            else:
                print(f"✅ Using organization: {organization.name} (ID: {organization.id})")
            
            # Create the admin user
            admin_user = User()
            admin_user.username = 'admin@noltrion.com'
            admin_user.email = 'admin@noltrion.com'
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'Noltrion'
            admin_user.role_id = admin_role.id
            admin_user.organization_id = organization.id
            admin_user.is_active = True
            admin_user.must_reset_password = False  # Set to False so they can use the temp password
            admin_user.set_password('Admin@123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ SUCCESS! Admin user created successfully!")
            print("="*60)
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"Password: Admin@123")
            print(f"Role: {admin_user.role.name}")
            print(f"Organization: {admin_user.organization.name}")
            print(f"Active: {admin_user.is_active}")
            print(f"Must Reset Password: {admin_user.must_reset_password}")
            print("="*60)
            print("\n🔐 The user can now login with these credentials!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to create admin user")
            print(f"Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    create_admin_user()