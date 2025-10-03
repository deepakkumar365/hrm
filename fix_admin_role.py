"""
Script to fix the admin user's role to use the correct ADMIN or SUPER_ADMIN role
"""

from app import app, db
from models import User, Role

def fix_admin_role():
    with app.app_context():
        try:
            # Find the user
            user = User.query.filter_by(username='admin@noltrion.com').first()
            
            if not user:
                print("❌ User not found!")
                return False
            
            print("\n" + "="*60)
            print("🔧 FIXING ADMIN ROLE")
            print("="*60)
            
            print(f"\nCurrent role: {user.role.name} (ID: {user.role_id})")
            
            # Find the SUPER_ADMIN role
            super_admin_role = Role.query.filter_by(name='SUPER_ADMIN').first()
            admin_role = Role.query.filter_by(name='ADMIN').first()
            
            if super_admin_role:
                print(f"\n✅ Found SUPER_ADMIN role (ID: {super_admin_role.id})")
                print(f"   Description: {super_admin_role.description}")
                
                # Update user to SUPER_ADMIN
                user.role_id = super_admin_role.id
                db.session.commit()
                
                print(f"\n✅ Updated user role to: {user.role.name} (ID: {user.role_id})")
                print(f"   This gives FULL SUPER ADMIN ACCESS!")
                
            elif admin_role:
                print(f"\n✅ Found ADMIN role (ID: {admin_role.id})")
                print(f"   Description: {admin_role.description}")
                
                # Update user to ADMIN
                user.role_id = admin_role.id
                db.session.commit()
                
                print(f"\n✅ Updated user role to: {user.role.name} (ID: {user.role_id})")
                print(f"   This gives ADMIN ACCESS!")
            else:
                print("\n⚠️  Neither SUPER_ADMIN nor ADMIN role found!")
                print("   Keeping current 'Admin' role")
            
            # Now test if the role check will work
            print("\n" + "="*60)
            print("🧪 TESTING ROLE ACCESS")
            print("="*60)
            
            # Refresh user from database
            db.session.refresh(user)
            
            print(f"\nUser: {user.username}")
            print(f"Role: {user.role.name} (ID: {user.role_id})")
            print(f"Role Description: {user.role.description}")
            
            # Test the role check that auth.py uses
            print(f"\n⚠️  WARNING: auth.py uses 'current_user.role in allowed_roles'")
            print(f"   This checks if Role OBJECT is in list, which will FAIL!")
            print(f"   user.role in ['Super Admin', 'Admin']: {user.role in ['Super Admin', 'Admin']}")
            print(f"   user.role in ['SUPER_ADMIN', 'ADMIN']: {user.role in ['SUPER_ADMIN', 'ADMIN']}")
            
            print(f"\n✅ CORRECT way: use 'current_user.role.name in allowed_roles'")
            print(f"   user.role.name in ['Super Admin', 'Admin']: {user.role.name in ['Super Admin', 'Admin']}")
            print(f"   user.role.name in ['SUPER_ADMIN', 'ADMIN']: {user.role.name in ['SUPER_ADMIN', 'ADMIN']}")
            
            print("\n" + "="*60)
            print("✅ Role update complete!")
            print("="*60)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    fix_admin_role()