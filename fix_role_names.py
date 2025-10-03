"""
Script to fix role names to match the code expectations
The code uses: 'Super Admin', 'Admin', 'Manager', 'User'
The database has: 'SUPER_ADMIN', 'ADMIN', 'HR_MANAGER', 'EMPLOYEE'
"""

from app import app, db
from models import Role, User

def fix_role_names():
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("🔧 FIXING ROLE NAMES")
            print("="*60)
            
            # Mapping of old names to new names
            role_mappings = {
                'SUPER_ADMIN': 'Super Admin',
                'ADMIN': 'Admin',
                'HR_MANAGER': 'Manager',
                'EMPLOYEE': 'User'
            }
            
            print("\n📋 Current roles in database:")
            all_roles = Role.query.all()
            for role in all_roles:
                print(f"   - {role.name} (ID: {role.id})")
            
            print("\n🔄 Updating role names...")
            for old_name, new_name in role_mappings.items():
                role = Role.query.filter_by(name=old_name).first()
                if role:
                    print(f"   ✅ Updating '{old_name}' → '{new_name}'")
                    role.name = new_name
                else:
                    print(f"   ⚠️  Role '{old_name}' not found, skipping")
            
            # Remove duplicate 'Admin' role if it exists
            admin_roles = Role.query.filter_by(name='Admin').all()
            if len(admin_roles) > 1:
                print(f"\n⚠️  Found {len(admin_roles)} 'Admin' roles, removing duplicates...")
                # Keep the first one, delete the rest
                for role in admin_roles[1:]:
                    # Update users with this role to use the first admin role
                    users_with_role = User.query.filter_by(role_id=role.id).all()
                    for user in users_with_role:
                        print(f"      Moving user {user.username} to primary Admin role")
                        user.role_id = admin_roles[0].id
                    
                    print(f"      Deleting duplicate Admin role (ID: {role.id})")
                    db.session.delete(role)
            
            db.session.commit()
            
            print("\n✅ Role names updated successfully!")
            
            print("\n📋 Updated roles in database:")
            all_roles = Role.query.all()
            for role in all_roles:
                print(f"   - {role.name} (ID: {role.id})")
                # Count users with this role
                user_count = User.query.filter_by(role_id=role.id).count()
                print(f"     Users with this role: {user_count}")
            
            # Verify our admin user
            print("\n👤 Verifying admin@noltrion.com user:")
            user = User.query.filter_by(username='admin@noltrion.com').first()
            if user:
                print(f"   Username: {user.username}")
                print(f"   Role: {user.role.name} (ID: {user.role_id})")
                print(f"   Active: {user.is_active}")
                
                # Test role check
                print(f"\n🧪 Testing role check:")
                print(f"   user.role.name in ['Super Admin', 'Admin']: {user.role.name in ['Super Admin', 'Admin']}")
                if user.role.name in ['Super Admin', 'Admin']:
                    print(f"   ✅ Role check PASSES! User has admin access!")
                else:
                    print(f"   ❌ Role check FAILS! User does NOT have admin access!")
            
            print("\n" + "="*60)
            print("✅ All done!")
            print("="*60)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    fix_role_names()