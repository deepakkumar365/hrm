"""
Script to test admin user access and role checking
"""

from app import app, db
from models import User, Role

def test_admin_access():
    with app.app_context():
        try:
            # Find the user
            user = User.query.filter_by(username='admin@noltrion.com').first()
            
            if not user:
                print("❌ User not found!")
                return False
            
            print("\n" + "="*60)
            print("🧪 TESTING ADMIN ACCESS")
            print("="*60)
            
            # Test 1: Check role object
            print("\n1️⃣ Testing role object:")
            print(f"   user.role = {user.role}")
            print(f"   type(user.role) = {type(user.role)}")
            print(f"   user.role.name = {user.role.name}")
            print(f"   user.role_name = {user.role_name}")
            
            # Test 2: Check if role comparison works
            print("\n2️⃣ Testing role comparisons:")
            allowed_roles = ['Super Admin', 'Admin']
            
            # This is how auth.py checks roles
            print(f"   Checking: user.role in {allowed_roles}")
            try:
                result = user.role in allowed_roles
                print(f"   Result: {result}")
                print(f"   ⚠️  This will FAIL because user.role is a Role object, not a string!")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # This is the correct way
            print(f"\n   Checking: user.role.name in {allowed_roles}")
            result = user.role.name in allowed_roles
            print(f"   Result: {result}")
            if result:
                print(f"   ✅ This works correctly!")
            
            # Test 3: Check what routes.py is doing
            print("\n3️⃣ Testing routes.py style checks:")
            print(f"   Checking: user.role in ['Super Admin', 'Admin']")
            try:
                result = user.role in ['Super Admin', 'Admin']
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Test 4: Check if there's a __eq__ method
            print("\n4️⃣ Checking Role object methods:")
            print(f"   Role object methods: {[m for m in dir(user.role) if not m.startswith('_')]}")
            
            # Test 5: Try string comparison
            print("\n5️⃣ Testing string comparison:")
            print(f"   user.role == 'Admin': {user.role == 'Admin'}")
            print(f"   user.role.name == 'Admin': {user.role.name == 'Admin'}")
            
            # Test 6: Check all admin-type roles
            print("\n6️⃣ All admin-type roles in database:")
            admin_roles = Role.query.filter(
                db.or_(
                    Role.name.ilike('%admin%'),
                    Role.name.ilike('%super%')
                )
            ).all()
            for role in admin_roles:
                print(f"   - {role.name} (ID: {role.id})")
            
            print("\n" + "="*60)
            print("✅ Test complete!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    test_admin_access()