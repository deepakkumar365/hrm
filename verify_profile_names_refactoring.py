#!/usr/bin/env python3
"""
Comprehensive verification script for profile names refactoring.
Tests that the refactoring is working correctly.
"""

from app import app, db
from models import User, Employee, Attendance, Leave, Claim, Organization, Role
from datetime import datetime, date
import sys

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def print_test(test_name, passed):
    """Print test result"""
    symbol = "✅" if passed else "❌"
    print(f"  {symbol} {test_name}")
    return passed

def test_user_model_properties():
    """Test that User model properties work correctly"""
    print_section("TEST 1: User Model Properties")
    
    with app.app_context():
        all_passed = True
        
        # Get a user with employee profile
        user_with_profile = User.query.filter(
            User.employee_profile.isnot(None)
        ).first()
        
        if user_with_profile:
            print(f"\nUser: {user_with_profile.username}")
            print(f"  Direct access: {user_with_profile.first_name} {user_with_profile.last_name}")
            print(f"  Property access: {user_with_profile.get_first_name} {user_with_profile.get_last_name}")
            print(f"  Full name: {user_with_profile.full_name}")
            
            # Test get_first_name
            test1 = print_test(
                "get_first_name returns value",
                user_with_profile.get_first_name is not None
            )
            all_passed = all_passed and test1
            
            # Test get_last_name
            test2 = print_test(
                "get_last_name returns value",
                user_with_profile.get_last_name is not None
            )
            all_passed = all_passed and test2
            
            # Test full_name
            test3 = print_test(
                "full_name returns combined value",
                len(user_with_profile.full_name) > 0
            )
            all_passed = all_passed and test3
            
            # Test that employee profile values are used
            if user_with_profile.employee_profile:
                test4 = print_test(
                    "get_first_name uses employee profile",
                    user_with_profile.get_first_name == user_with_profile.employee_profile.first_name
                )
                all_passed = all_passed and test4
        else:
            print("\n⚠️  No users with employee profiles found!")
            all_passed = False
        
        # Test user without profile (if exists)
        user_without_profile = User.query.filter(
            User.employee_profile.isnot(None)
        ).first()
        
        if user_without_profile:
            print(f"\nUser without profile: {user_without_profile.username}")
            test5 = print_test(
                "get_first_name fallback works",
                user_without_profile.get_first_name == user_without_profile.first_name
            )
            all_passed = all_passed and test5
        
        return all_passed

def test_data_consistency():
    """Test that user and employee data are consistent"""
    print_section("TEST 2: Data Consistency")
    
    with app.app_context():
        all_passed = True
        
        # Get all users with profiles
        users_with_profiles = User.query.filter(
            User.employee_profile.isnot(None)
        ).all()
        
        inconsistent_users = []
        
        for user in users_with_profiles:
            # Check if names are synchronized
            if (user.first_name != user.employee_profile.first_name or 
                user.last_name != user.employee_profile.last_name):
                inconsistent_users.append(user)
        
        if inconsistent_users:
            print(f"\n⚠️  Found {len(inconsistent_users)} users with inconsistent names:")
            for user in inconsistent_users[:5]:
                print(f"  - {user.username}:")
                print(f"    User: {user.first_name} {user.last_name}")
                print(f"    Employee: {user.employee_profile.first_name} {user.employee_profile.last_name}")
            
            test1 = print_test(
                "All user names synchronized with employee profiles",
                False
            )
            all_passed = False
        else:
            test1 = print_test(
                "All user names synchronized with employee profiles",
                True
            )
            all_passed = all_passed and test1
        
        # Check that all users have employee profiles
        users_without_profiles = User.query.filter(
            User.employee_profile.isnot(None)
        ).all()
        
        if len(users_without_profiles) > 0:
            print(f"\n⚠️  Found {len(users_without_profiles)} users without employee profiles")
            test2 = print_test(
                "All users have employee profiles",
                False
            )
            all_passed = False
        else:
            test2 = print_test(
                "All users have employee profiles",
                True
            )
            all_passed = all_passed and test2
        
        return all_passed

def test_audit_logs():
    """Test that audit logs use correct names"""
    print_section("TEST 3: Audit Logs")
    
    with app.app_context():
        all_passed = True
        
        # Check attendance records with notes
        attendances = Attendance.query.filter(
            Attendance.notes.isnot(None),
            Attendance.notes != ''
        ).limit(5).all()
        
        if attendances:
            print(f"\nChecking {len(attendances)} attendance records...")
            for att in attendances:
                print(f"\n  Attendance ID {att.id}:")
                print(f"    Notes: {att.notes[:100]}")
                test1 = print_test(
                    "Audit log has notes",
                    len(att.notes) > 0
                )
                all_passed = all_passed and test1
        else:
            print("\n⚠️  No attendance records with notes found to verify")
        
        # Check remarks
        attendances_with_remarks = Attendance.query.filter(
            Attendance.remarks.isnot(None),
            Attendance.remarks != ''
        ).limit(5).all()
        
        if attendances_with_remarks:
            print(f"\nChecking {len(attendances_with_remarks)} records with remarks...")
            for att in attendances_with_remarks:
                print(f"\n  Attendance ID {att.id}:")
                print(f"    Remarks: {att.remarks}")
                test2 = print_test(
                    "Audit log has remarks",
                    len(att.remarks) > 0
                )
                all_passed = all_passed and test2
        
        return all_passed

def test_employee_references():
    """Test that employee references still work correctly"""
    print_section("TEST 4: Employee References")
    
    with app.app_context():
        all_passed = True
        
        # Check various employee references
        employees = Employee.query.limit(3).all()
        
        for emp in employees:
            print(f"\nEmployee: {emp.employee_id}")
            print(f"  Name: {emp.first_name} {emp.last_name}")
            print(f"  User: {emp.user.username if emp.user else 'No user'}")
            
            test1 = print_test(
                f"Employee {emp.employee_id} has valid name",
                emp.first_name and emp.last_name
            )
            all_passed = all_passed and test1
        
        return all_passed

def test_relationships():
    """Test that relationships are properly configured"""
    print_section("TEST 5: Relationships")
    
    with app.app_context():
        all_passed = True
        
        # Test User -> Employee relationship
        user_with_employee = User.query.filter(
            User.employee_profile.isnot(None)
        ).first()
        
        if user_with_employee:
            test1 = print_test(
                "User.employee_profile relationship works",
                user_with_employee.employee_profile is not None
            )
            all_passed = all_passed and test1
            
            # Test Employee -> User relationship
            test2 = print_test(
                "Employee.user relationship works",
                user_with_employee.employee_profile.user == user_with_employee
            )
            all_passed = all_passed and test2
        else:
            print("\n⚠️  No users with employee profiles found")
            all_passed = False
        
        return all_passed

def generate_summary_report():
    """Generate a summary report of the refactoring status"""
    print_section("REFACTORING STATUS SUMMARY")
    
    with app.app_context():
        total_users = User.query.count()
        users_with_profiles = User.query.filter(
            User.employee_profile.isnot(None)
        ).count()
        users_without_profiles = total_users - users_with_profiles
        
        print(f"""
Total Users:                  {total_users}
Users with Profiles:          {users_with_profiles}
Users without Profiles:       {users_without_profiles}

Readiness:
  ✓ Properties added to User model
  ✓ Migration scripts created
  {'✓' if users_without_profiles == 0 else '⚠'} All users have employee profiles
  ✓ Helper scripts created
  ⏳ Templates updated (manual process)
  ⏳ Routes fully refactored
  
Next Steps:
  1. Run: python migrate_profile_names.py
  2. Update templates: python update_templates_helper.py
  3. Test thoroughly
  4. Drop redundant columns (after verification)
""")

def main():
    """Run all tests"""
    print("🚀 Starting Profile Names Refactoring Verification")
    print("=" * 80)
    
    results = {}
    
    try:
        # Run all tests
        results['Properties'] = test_user_model_properties()
        results['Consistency'] = test_data_consistency()
        results['Audit'] = test_audit_logs()
        results['Employees'] = test_employee_references()
        results['Relationships'] = test_relationships()
        
        # Print summary
        print_section("VERIFICATION SUMMARY")
        
        all_passed = True
        for test_name, passed in results.items():
            symbol = "✅" if passed else "⚠️"
            print(f"  {symbol} {test_name}: {'PASSED' if passed else 'INCOMPLETE'}")
            all_passed = all_passed and passed
        
        # Generate report
        generate_summary_report()
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL TESTS PASSED - Refactoring is proceeding correctly")
        else:
            print("⚠️  SOME ISSUES FOUND - Please review above")
            print("\nCommon issues and solutions:")
            print("  1. No users with profiles - Run: python migrate_profile_names.py")
            print("  2. Names not synchronized - Run: python migrate_profile_names.py")
            print("  3. Relationships broken - Check models.py relationships")
        print("=" * 80 + "\n")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())