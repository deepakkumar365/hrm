"""
Script to fix role names to match the code expectations
Step 1: Remove duplicate roles
Step 2: Rename remaining roles to match code
"""

from app import app, db
from models import Role, User

def fix_role_names():
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("🔧 FIXING ROLE NAMES")
            print("="*60)
            
            print("\n📋 Current roles in database:")
            all_roles = Role.query.all()
            for role in all_roles:
                user_count = User.query.filter_by(role_id=role.id).count()
                print(f"   - {role.name} (ID: {role.id}) - {user_count} users")
            
            # Step 1: Remove duplicate 'Admin' role (ID: 5)
            print("\n🗑️  Step 1: Removing duplicate roles...")
            duplicate_admin = Role.query.filter_by(id=5).first()
            if duplicate_admin:
                # Move users from duplicate Admin (ID: 5) to SUPER_ADMIN (ID: 1)
                users_with_duplicate = User.query.filter_by(role_id=5).all()
                super_admin_role = Role.query.filter_by(name='SUPER_ADMIN').first()
                
                if super_admin_role:
                    for user in users_with_duplicate:
                        print(f"   Moving user {user.username} from '{duplicate_admin.name}' to '{super_admin_role.name}'")
                        user.role_id = super_admin_role.id
                    
                    db.session.flush()
                    
                    print(f"   Deleting duplicate 'Admin' role (ID: 5)")
                    db.session.delete(duplicate_admin)
                    db.session.flush()
            
            # Step 2: Rename roles to match code expectations
            print("\n🔄 Step 2: Renaming roles...")
            role_mappings = {
                'SUPER_ADMIN': 'Super Admin',
                'ADMIN': 'Admin',
                'HR_MANAGER': 'Manager',
                'EMPLOYEE': 'User'
            }
            
            for old_name, new_name in role_mappings.items():
                role = Role.query.filter_by(name=old_name).first()
                if role:
                    print(f"   ✅ Renaming '{old_name}' → '{new_name}' (ID: {role.id})")
                    role.name = new_name
                else:
                    print(f"   ⚠️  Role '{old_name}' not found, skipping")
            
            db.session.commit()
            
            print("\n✅ Role names updated successfully!")
            
            print("\n📋 Updated roles in database:")
            all_roles = Role.query.all()
            for role in all_roles:
                user_count = User.query.filter_by(role_id=role.id).count()
                print(f"   - {role.name} (ID: {role.id}) - {user_count} users")
            
            # Verify our admin user
            print("\n👤 Verifying admin@noltrion.com user:")
            user = User.query.filter_by(username='admin@noltrion.com').first()
            if user:
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.role.name} (ID: {user.role_id})")
                print(f"   Active: {user.is_active}")
                print(f"   Password: Admin@123")
                
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
            print("\n📝 SUMMARY:")
            print("   Username: admin@noltrion.com")
            print("   Password: Admin@123")
            print("   Role: Super Admin (full access)")
            print("   Status: Active and ready to use!")
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