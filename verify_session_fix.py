#!/usr/bin/env python3
"""
Session/Logout Fix Verification Script

This script verifies that all session/logout fixes are properly implemented
in the codebase before deployment.

Usage:
    python verify_session_fix.py
"""

import os
import sys
import re
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print_success(f"File found: {filepath}")
        return True
    else:
        print_error(f"File not found: {filepath}")
        return False

def check_code_pattern(filepath, pattern, description, required=True):
    """Check if a code pattern exists in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                print_success(f"{description}")
                return True
            else:
                if required:
                    print_error(f"{description} - NOT FOUND")
                else:
                    print_warning(f"{description} - NOT FOUND (optional)")
                return False
    except Exception as e:
        print_error(f"Error reading {filepath}: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 Session/Logout Fix Verification")
    print("="*70 + "\n")

    # Get project root
    project_root = Path(__file__).parent
    print_info(f"Project root: {project_root}\n")

    # Track overall status
    all_checks_passed = True

    # Check 1: Verify files exist
    print("📁 Step 1: Checking if required files exist...")
    print("-" * 70)
    
    files_to_check = [
        'routes.py',
        'app.py',
        'auth.py',
        'SESSION_LOGOUT_FIX.md',
        'DEPLOYMENT_VERIFICATION.md'
    ]
    
    for filename in files_to_check:
        filepath = project_root / filename
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    print()

    # Check 2: Verify logout function
    print("🚪 Step 2: Checking logout function...")
    print("-" * 70)
    
    routes_file = project_root / 'routes.py'
    
    checks = [
        (r"@app\.route\('/logout'\)", "Logout route defined"),
        (r"logout_user\(\)", "logout_user() called"),
        (r"session\.clear\(\)", "session.clear() called"),
        (r"response\.headers\['Cache-Control'\]\s*=\s*['\"]no-cache", "Cache-Control header set in logout"),
    ]
    
    for pattern, description in checks:
        if not check_code_pattern(routes_file, pattern, description):
            all_checks_passed = False
    
    print()

    # Check 3: Verify login function
    print("🔐 Step 3: Checking login function...")
    print("-" * 70)
    
    checks = [
        (r"@app\.route\('/login'", "Login route defined"),
        (r"session\.clear\(\).*login_user", "session.clear() before login_user()", True),
        (r"login_user\([^,]+,\s*remember=False", "remember=False in login_user()"),
        (r"login_user\([^,]+,.*fresh=True", "fresh=True in login_user()"),
        (r"response\.headers\['Cache-Control'\].*no-cache", "Cache-Control header in login redirect"),
    ]
    
    for pattern, description, *required in checks:
        req = required[0] if required else True
        if not check_code_pattern(routes_file, pattern, description, req):
            if req:
                all_checks_passed = False
    
    print()

    # Check 4: Verify security headers middleware
    print("🛡️  Step 4: Checking security headers middleware...")
    print("-" * 70)
    
    checks = [
        (r"@app\.after_request", "after_request decorator found"),
        (r"def add_security_headers", "add_security_headers function defined"),
        (r"response\.headers\['Cache-Control'\]", "Cache-Control header set"),
        (r"response\.headers\['Pragma'\]", "Pragma header set"),
        (r"response\.headers\['Expires'\]", "Expires header set"),
    ]
    
    for pattern, description in checks:
        if not check_code_pattern(routes_file, pattern, description):
            all_checks_passed = False
    
    print()

    # Check 5: Verify session configuration
    print("⚙️  Step 5: Checking session configuration...")
    print("-" * 70)
    
    app_file = project_root / 'app.py'
    
    checks = [
        (r"PERMANENT_SESSION_LIFETIME.*timedelta", "PERMANENT_SESSION_LIFETIME configured"),
        (r"SESSION_COOKIE_SECURE", "SESSION_COOKIE_SECURE configured"),
        (r"SESSION_COOKIE_HTTPONLY.*True", "SESSION_COOKIE_HTTPONLY set to True"),
        (r"SESSION_COOKIE_SAMESITE.*['\"]Lax['\"]", "SESSION_COOKIE_SAMESITE set to Lax"),
        (r"SESSION_REFRESH_EACH_REQUEST.*False", "SESSION_REFRESH_EACH_REQUEST set to False"),
    ]
    
    for pattern, description in checks:
        if not check_code_pattern(app_file, pattern, description):
            all_checks_passed = False
    
    print()

    # Check 6: Verify Flask-Login configuration
    print("🔑 Step 6: Checking Flask-Login configuration...")
    print("-" * 70)
    
    auth_file = project_root / 'auth.py'
    
    checks = [
        (r"login_manager\s*=\s*LoginManager\(\)", "LoginManager initialized"),
        (r"login_manager\.session_protection\s*=\s*['\"]strong['\"]", "session_protection set to 'strong'"),
        (r"login_manager\.login_view", "login_view configured"),
        (r"@login_manager\.user_loader", "user_loader decorator found"),
    ]
    
    for pattern, description in checks:
        if not check_code_pattern(auth_file, pattern, description):
            all_checks_passed = False
    
    print()

    # Check 7: Verify documentation
    print("📚 Step 7: Checking documentation...")
    print("-" * 70)
    
    doc_file = project_root / 'SESSION_LOGOUT_FIX.md'
    
    if check_file_exists(doc_file):
        checks = [
            (r"Problem Description", "Problem description section exists"),
            (r"Root Causes", "Root causes section exists"),
            (r"Solutions Implemented", "Solutions section exists"),
            (r"Testing", "Testing section exists"),
        ]
        
        for pattern, description in checks:
            check_code_pattern(doc_file, pattern, description, required=False)
    
    print()

    # Final summary
    print("="*70)
    if all_checks_passed:
        print_success("🎉 All critical checks passed! Your code is ready for deployment.")
        print()
        print_info("Next steps:")
        print("  1. Commit your changes: git add . && git commit -m 'Fix session/logout issues'")
        print("  2. Push to repository: git push")
        print("  3. Monitor Render deployment")
        print("  4. Test the fix on production")
        print()
        return 0
    else:
        print_error("❌ Some checks failed. Please review the errors above.")
        print()
        print_warning("Common issues:")
        print("  - Make sure all files are saved")
        print("  - Check for typos in function names")
        print("  - Verify imports are correct")
        print("  - Review the SESSION_LOGOUT_FIX.md for implementation details")
        print()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)