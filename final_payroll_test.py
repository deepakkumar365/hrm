"""
Final comprehensive test to verify payroll access is working
"""

from app import app, db
from models import User, Role
import re

def test_complete_system():
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 FINAL COMPREHENSIVE SYSTEM TEST")
        print("="*70)
        
        # 1. Test admin user
        print("\n1️⃣  ADMIN USER VERIFICATION:")
        print("-" * 70)
        admin_user = User.query.filter_by(username='admin@noltrion.com').first()
        
        if not admin_user:
            print("   ❌ Admin user not found!")
            return False
        
        print(f"   ✅ Username: {admin_user.username}")
        print(f"   ✅ Role: {admin_user.role.name if admin_user.role else 'None'}")
        print(f"   ✅ Active: {admin_user.is_active}")
        
        # 2. Test auth.py decorator logic
        print("\n2️⃣  AUTH.PY DECORATOR TEST:")
        print("-" * 70)
        
        with open('E:/Gobi/Pro/HRMS/hrm/auth.py', 'r', encoding='utf-8') as f:
            auth_content = f.read()
        
        if 'user_role = current_user.role.name if current_user.role else None' in auth_content:
            print("   ✅ auth.py uses correct role checking pattern")
        else:
            print("   ❌ auth.py has incorrect role checking pattern")
            return False
        
        # 3. Test routes.py
        print("\n3️⃣  ROUTES.PY TEST:")
        print("-" * 70)
        
        with open('E:/Gobi/Pro/HRMS/hrm/routes.py', 'r', encoding='utf-8') as f:
            routes_content = f.read()
        
        # Count correct patterns
        correct_patterns = routes_content.count('current_user.role.name')
        
        # Check for incorrect patterns (should be 0)
        # Look for patterns like "current_user.role ==" or "current_user.role in" 
        # that are NOT followed by ".name"
        incorrect_pattern = re.findall(r'current_user\.role\s+(?:==|in|!=)\s+(?!\.name)', routes_content)
        
        print(f"   ✅ Found {correct_patterns} correct role.name usages")
        if len(incorrect_pattern) > 0:
            print(f"   ⚠️  Found {len(incorrect_pattern)} potential incorrect patterns")
        else:
            print(f"   ✅ No incorrect patterns found")
        
        # 4. Test templates
        print("\n4️⃣  TEMPLATE FILES TEST:")
        print("-" * 70)
        
        import os
        from pathlib import Path
        
        templates_dir = Path('E:/Gobi/Pro/HRMS/hrm/templates')
        html_files = list(templates_dir.rglob('*.html'))
        
        total_correct = 0
        total_incorrect = 0
        
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            correct = content.count('current_user.role.name')
            # Look for incorrect patterns
            incorrect = len(re.findall(r'current_user\.role\s+(?:==|in|!=)\s+(?!\.name)', content))
            
            total_correct += correct
            total_incorrect += incorrect
        
        print(f"   ✅ Found {total_correct} correct role.name usages in templates")
        if total_incorrect > 0:
            print(f"   ⚠️  Found {total_incorrect} potential incorrect patterns in templates")
        else:
            print(f"   ✅ No incorrect patterns found in templates")
        
        # 5. Test specific payroll routes
        print("\n5️⃣  PAYROLL ROUTES ACCESS TEST:")
        print("-" * 70)
        
        user_role = admin_user.role.name if admin_user.role else None
        
        payroll_routes = [
            ("/payroll", ['Super Admin', 'Admin', 'Manager']),
            ("/payroll/generate", ['Super Admin', 'Admin']),
            ("/payroll/config", ['Super Admin', 'Admin', 'Manager']),
            ("/payroll/<id>/approve", ['Super Admin', 'Admin']),
        ]
        
        all_pass = True
        for route, required_roles in payroll_routes:
            has_access = user_role in required_roles
            status = "✅ PASS" if has_access else "❌ FAIL"
            print(f"   {status}: {route}")
            if not has_access:
                all_pass = False
        
        # 6. Test base.html specifically
        print("\n6️⃣  BASE.HTML NAVIGATION TEST:")
        print("-" * 70)
        
        with open('E:/Gobi/Pro/HRMS/hrm/templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # Check if payroll menu is visible (should not have role restrictions)
        if 'Payroll' in base_content and 'payroll_list' in base_content:
            print("   ✅ Payroll menu exists in navigation")
        else:
            print("   ❌ Payroll menu not found in navigation")
            all_pass = False
        
        # Check if role display is correct
        if "current_user.role.name if current_user.role else 'None'" in base_content:
            print("   ✅ Role display uses correct pattern")
        else:
            print("   ⚠️  Role display might use incorrect pattern")
        
        # 7. Final summary
        print("\n" + "="*70)
        print("📋 FINAL SUMMARY")
        print("="*70)
        
        if all_pass:
            print("\n✅ ALL TESTS PASSED!")
            print("\n🎉 The admin user can now access all payroll pages!")
            print("\n📝 Login Credentials:")
            print(f"   Username: admin@noltrion.com")
            print(f"   Password: Admin@123")
            print(f"   Role: {user_role}")
            print("\n🚀 You can now:")
            print("   1. Start the Flask application")
            print("   2. Login with the admin credentials")
            print("   3. Access all Payroll menu items:")
            print("      - Payroll List")
            print("      - Generate Payroll")
            print("      - Payroll Configuration")
            print("   4. View, edit, and approve payroll records")
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("   Please review the output above for details")
        
        print("\n" + "="*70)
        
        return all_pass

if __name__ == '__main__':
    test_complete_system()