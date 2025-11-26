#!/usr/bin/env python3
"""
Timezone Display Implementation Verification Script
Checks that all timezone display changes are correctly implemented
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🌍 TIMEZONE DISPLAY IMPLEMENTATION VERIFICATION")
print("=" * 70)

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CHECK = '✅'
CROSS = '❌'
WARN = '⚠️ '

def check_file_contains(filepath, search_text, description):
    """Check if a file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"{GREEN}{CHECK}{RESET} {description}")
                return True
            else:
                print(f"{RED}{CROSS}{RESET} {description}")
                return False
    except Exception as e:
        print(f"{RED}{CROSS}{RESET} Error checking file: {e}")
        return False

def check_database_column():
    """Check if timezone column exists in company table"""
    try:
        os.environ['FLASK_APP'] = 'main.py'
        from app import app, db
        from sqlalchemy import inspect
        
        with app.app_context():
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('hrm_company')]
            
            if 'timezone' in columns:
                print(f"{GREEN}{CHECK}{RESET} Database column 'timezone' exists in hrm_company table")
                return True
            else:
                print(f"{RED}{CROSS}{RESET} Database column 'timezone' NOT found in hrm_company")
                print(f"    Available columns: {', '.join(columns[-5:])}")
                return False
    except Exception as e:
        print(f"{YELLOW}{WARN}{RESET} Could not verify database: {e}")
        return False

print("\n" + BLUE + "1. CHECKING BACKEND FILES" + RESET)
print("-" * 70)

# Check routes_ot.py for timezone handling
routes_checks = [
    (
        'routes_ot.py',
        'company.timezone',
        'Company timezone retrieval in routes_ot.py'
    ),
    (
        'routes_ot.py',
        'company_timezone=company_timezone',
        'Timezone passed to template in routes_ot.py'
    ),
]

backend_passes = 0
for filepath, search_text, description in routes_checks:
    full_path = project_root / filepath
    if check_file_contains(full_path, search_text, description):
        backend_passes += 1

print("\n" + BLUE + "2. CHECKING FRONTEND FILES" + RESET)
print("-" * 70)

# Check templates/ot/mark_attendance.html for timezone features
template_checks = [
    (
        'templates/ot/mark_attendance.html',
        'company_timezone',
        'Company timezone variable in template'
    ),
    (
        'templates/ot/mark_attendance.html',
        'id="liveClock"',
        'Live clock display element'
    ),
    (
        'templates/ot/mark_attendance.html',
        'id="clockTimezone"',
        'Clock timezone label element'
    ),
    (
        'templates/ot/mark_attendance.html',
        'function getTimeInTimezone(timezone)',
        'Timezone conversion function'
    ),
    (
        'templates/ot/mark_attendance.html',
        'function updateLiveClock()',
        'Live clock update function'
    ),
    (
        'templates/ot/mark_attendance.html',
        'setInterval(updateLiveClock, 1000)',
        'Clock update interval (every second)'
    ),
    (
        'templates/ot/mark_attendance.html',
        'Intl.DateTimeFormat',
        'IANA timezone support via Intl API'
    ),
    (
        'templates/ot/mark_attendance.html',
        'Asia/Kolkata',
        'India timezone support'
    ),
    (
        'templates/ot/mark_attendance.html',
        'Asia/Singapore',
        'Singapore timezone support'
    ),
    (
        'templates/ot/mark_attendance.html',
        'Your company timezone',
        'Company timezone display in help text'
    ),
]

frontend_passes = 0
for filepath, search_text, description in template_checks:
    full_path = project_root / filepath
    if check_file_contains(full_path, search_text, description):
        frontend_passes += 1

print("\n" + BLUE + "3. CHECKING DATABASE SCHEMA" + RESET)
print("-" * 70)

db_passes = 0
if check_database_column():
    db_passes += 1

print("\n" + BLUE + "4. CHECKING TIMEZONE FEATURES" + RESET)
print("-" * 70)

feature_checks = [
    (
        'templates/ot/mark_attendance.html',
        "formatted12: new Intl.DateTimeFormat",
        'Time formatting in 12-hour format (HH:MM AM/PM)'
    ),
    (
        'templates/ot/mark_attendance.html',
        'setCurrentTime(fieldId)',
        'Set current time button functionality'
    ),
    (
        'templates/ot/mark_attendance.html',
        "console.log(`✅ Set ${fieldId}",
        'Debug logging for time setting'
    ),
]

feature_passes = 0
for filepath, search_text, description in feature_checks:
    full_path = project_root / filepath
    if check_file_contains(full_path, search_text, description):
        feature_passes += 1

print("\n" + "=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)

total_checks = len(routes_checks) + len(template_checks) + db_passes + len(feature_checks)
total_passes = backend_passes + frontend_passes + db_passes + feature_passes

print(f"\n{BLUE}Backend Checks:{RESET} {backend_passes}/{len(routes_checks)}")
print(f"{BLUE}Frontend Checks:{RESET} {frontend_passes}/{len(template_checks)}")
print(f"{BLUE}Database Checks:{RESET} {db_passes}/1")
print(f"{BLUE}Feature Checks:{RESET} {feature_passes}/{len(feature_checks)}")

print(f"\n{BLUE}Total:{RESET} {total_passes}/{total_checks} checks passed")

if total_passes == total_checks:
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}{CHECK} ALL CHECKS PASSED! Timezone display implementation is complete.{RESET}")
    print(f"{GREEN}{'='*70}{RESET}")
    print("\n🚀 Next Steps:")
    print("   1. Test in browser: Navigate to OT Management > Mark OT Attendance")
    print("   2. Verify live clock displays current time in your timezone")
    print("   3. Check that timezone dropdown auto-selects company timezone")
    print("   4. Click 'Set In' and 'Set Out' buttons to test time capture")
    print("   5. Verify console logs (F12 > Console) for debug info")
else:
    print(f"\n{RED}{'='*70}{RESET}")
    print(f"{YELLOW}{WARN} Some checks failed. Please review the output above.{RESET}")
    print(f"{RED}{'='*70}{RESET}")

print("\n📝 For detailed information, see: TIMEZONE_DISPLAY_IMPLEMENTATION.md\n")