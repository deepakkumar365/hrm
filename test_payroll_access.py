"""
Test script to verify payroll access for admin user
"""

from app import app, db
from models import User, Role

def test_payroll_access():
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 TESTING PAYROLL ACCESS FOR ADMIN USER")
        print("="*70)
        
        # Get the admin user
        admin_user = User.query.filter_by(username='admin@noltrion.com').first()
        
        if not admin_user:
            print("\n❌ Admin user not found!")
            return False
        
        print(f"\n👤 User: {admin_user.username}")
        print(f"   Role ID: {admin_user.role_id}")
        print(f"   Role Object: {admin_user.role}")
        print(f"   Role Name: {admin_user.role.name if admin_user.role else 'None'}")
        
        # Test the role check logic used in @require_role decorator
        print("\n🧪 Testing @require_role(['Super Admin', 'Admin']) logic:")
        print("-" * 70)
        
        allowed_roles = ['Super Admin', 'Admin']
        user_role = admin_user.role.name if admin_user.role else None
        
        print(f"   allowed_roles = {allowed_roles}")
        print(f"   user_role = '{user_role}'")
        print(f"   user_role in allowed_roles = {user_role in allowed_roles}")
        
        if user_role in allowed_roles:
            print("\n   ✅ PASS: User SHOULD have access to payroll pages")
        else:
            print("\n   ❌ FAIL: User SHOULD NOT have access to payroll pages")
            print(f"   ⚠️  User role '{user_role}' is not in {allowed_roles}")
        
        # Test all payroll-related role requirements
        print("\n🔍 Testing all payroll route decorators:")
        print("-" * 70)
        
        payroll_routes = [
            ("/payroll", ['Super Admin', 'Admin', 'Manager']),
            ("/payroll/generate", ['Super Admin', 'Admin']),
            ("/payroll/config", ['Super Admin', 'Admin', 'Manager']),
            ("/payroll/<id>/approve", ['Super Admin', 'Admin']),
        ]
        
        for route, required_roles in payroll_routes:
            has_access = user_role in required_roles
            status = "✅ ALLOWED" if has_access else "❌ DENIED"
            print(f"   {status}: {route}")
            print(f"            Required: {required_roles}")
            print(f"            User has: '{user_role}'")
            print()
        
        # Check if there are any other users with similar issues
        print("\n📋 Checking all users with Admin or Super Admin roles:")
        print("-" * 70)
        
        admin_users = User.query.join(Role).filter(
            Role.name.in_(['Admin', 'Super Admin'])
        ).all()
        
        for user in admin_users:
            role_name = user.role.name if user.role else 'None'
            print(f"   User: {user.username}")
            print(f"   Role: {role_name} (ID: {user.role_id})")
            print(f"   Active: {user.is_active}")
            print(f"   Can access payroll: {role_name in ['Super Admin', 'Admin']}")
            print()
        
        print("="*70)
        print("✅ Test Complete")
        print("="*70)
        
        return True

if __name__ == '__main__':
    test_payroll_access()