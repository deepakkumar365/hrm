#!/usr/bin/env python3
"""Verify the syntax fix was applied correctly"""

import sys

def verify_routes_syntax():
    """Verify routes.py has valid Python syntax"""
    print("=" * 60)
    print("🔍 Verifying routes.py Syntax")
    print("=" * 60)
    
    try:
        # Try to compile the file
        with open('D:/Projects/HRMS/hrm/routes.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'routes.py', 'exec')
        print("\n✅ SUCCESS: routes.py has valid Python syntax!")
        print("   The application should start without syntax errors.")
        return True
        
    except SyntaxError as e:
        print(f"\n❌ SYNTAX ERROR in routes.py:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        return False
        
    except Exception as e:
        print(f"\n⚠️  Error checking syntax: {e}")
        return False

def verify_claims_approve_complete():
    """Verify the claims_approve function is complete"""
    print("\n" + "=" * 60)
    print("🔍 Verifying claims_approve Function")
    print("=" * 60)
    
    try:
        with open('D:/Projects/HRMS/hrm/routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        checks = {
            "def claims_approve(claim_id):": "Function definition",
            "if action == 'approve':": "Approve branch",
            "elif action == 'reject':": "Reject branch", 
            "db.session.commit()": "Database commit",
            "return redirect(url_for('claims_list'))": "Redirect return",
            "except Exception as e:": "Exception handler",
        }
        
        all_present = True
        for check, description in checks.items():
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - MISSING!")
                all_present = False
        
        if all_present:
            print("\n✅ All required components present in claims_approve!")
            return True
        else:
            print("\n⚠️  Some components are missing")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying function: {e}")
        return False

def main():
    """Run all verifications"""
    syntax_ok = verify_routes_syntax()
    function_ok = verify_claims_approve_complete()
    
    print("\n" + "=" * 60)
    print("📋 Verification Summary")
    print("=" * 60)
    
    if syntax_ok and function_ok:
        print("\n🎉 All checks passed! Application is ready to run.")
        print("\n   Run: python main.py")
        return 0
    else:
        print("\n⚠️  Some issues were detected. Please apply the fix:")
        print("\n   Run: python auto_syntax_fix.py")
        print("   Then: python main.py")
        return 1

if __name__ == '__main__':
    sys.exit(main())