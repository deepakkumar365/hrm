#!/usr/bin/env python3
"""
Migration script: Move profile names from hrm_users to hrm_employee
This script ensures all users have employee profiles with proper first_name and last_name.
"""

from app import app, db
from models import User, Employee, Organization, Role
from datetime import date
import sys

def migrate_profile_names():
    """
    Perform data migration:
    1. Check for users without employee profiles
    2. Create missing employee profiles
    3. Verify name consistency
    4. Report migration status
    """
    with app.app_context():
        print("=" * 70)
        print("PROFILE NAMES MIGRATION: Moving names from hrm_users to hrm_employee")
        print("=" * 70)
        
        # Get statistics
        total_users = User.query.count()
        users_with_profiles = User.query.filter(User.employee_profile.isnot(None)).count()
        users_without_profiles = total_users - users_with_profiles
        
        print(f"\n📊 CURRENT STATUS:")
        print(f"   Total users: {total_users}")
        print(f"   Users with employee profiles: {users_with_profiles}")
        print(f"   Users without employee profiles: {users_without_profiles}")
        
        if users_without_profiles == 0:
            print("\n✅ All users already have employee profiles!")
            return True
        
        print(f"\n⚠️  Creating employee profiles for {users_without_profiles} users...")
        
        # Get users without profiles
        users_without_profiles_list = User.query.filter(
            User.employee_profile.isnot(None)
        ).all()
        
        try:
            created_count = 0
            failed_users = []
            
            for user in User.query.all():
                if user.employee_profile:
                    continue  # Already has profile
                
                try:
                    # Get employee ID
                    next_emp_id = db.session.query(Employee).count() + 1
                    employee_id = f"EMP{next_emp_id:06d}"
                    
                    # Create employee profile
                    employee = Employee(
                        employee_id=employee_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        nric='PENDING',  # Placeholder - should be updated manually
                        position='To Be Determined',  # Placeholder
                        hire_date=date.today(),
                        employment_type='Full-time',
                        work_permit_type='Unknown',
                        basic_salary=0,  # Placeholder
                        user_id=user.id,
                        organization_id=user.organization_id,
                        is_active=user.is_active
                    )
                    
                    db.session.add(employee)
                    db.session.flush()
                    
                    created_count += 1
                    print(f"   ✓ Created profile for {user.username} ({user.first_name} {user.last_name})")
                    
                except Exception as e:
                    failed_users.append((user.username, str(e)))
                    print(f"   ✗ Failed for {user.username}: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ MIGRATION COMPLETE:")
            print(f"   Successfully created: {created_count} profiles")
            
            if failed_users:
                print(f"   ⚠️  Failed to create: {len(failed_users)} profiles")
                for username, error in failed_users:
                    print(f"      - {username}: {error}")
            
            return len(failed_users) == 0
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ MIGRATION FAILED: {str(e)}")
            return False

def verify_migration():
    """Verify that migration was successful"""
    with app.app_context():
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        
        total_users = User.query.count()
        users_with_profiles = User.query.filter(User.employee_profile.isnot(None)).count()
        
        print(f"\nFinal Status:")
        print(f"   Total users: {total_users}")
        print(f"   Users with profiles: {users_with_profiles}")
        
        if total_users == users_with_profiles:
            print("\n✅ All users now have employee profiles!")
            
            # Show sample of name sources
            print("\nSample user profiles:")
            for user in User.query.limit(5).all():
                if user.employee_profile:
                    print(f"   - {user.username}: User({user.first_name} {user.last_name}) → "
                          f"Employee({user.employee_profile.first_name} {user.employee_profile.last_name})")
            
            return True
        else:
            print(f"\n⚠️  Still {total_users - users_with_profiles} users without profiles")
            return False

def sync_user_names_with_employee():
    """
    Sync user names with employee profile names.
    For display purposes, ensure both tables have same first/last names.
    """
    with app.app_context():
        print("\n" + "=" * 70)
        print("SYNCING USER NAMES WITH EMPLOYEE PROFILES")
        print("=" * 70)
        
        synced_count = 0
        
        for user in User.query.all():
            if user.employee_profile:
                old_first = user.first_name
                old_last = user.last_name
                
                # Update user columns to match employee (for data consistency)
                user.first_name = user.employee_profile.first_name
                user.last_name = user.employee_profile.last_name
                
                if (old_first != user.first_name or old_last != user.last_name):
                    print(f"   Synced {user.username}: "
                          f"({old_first} {old_last}) → "
                          f"({user.first_name} {user.last_name})")
                    synced_count += 1
        
        db.session.commit()
        print(f"\n✅ Synced {synced_count} user names with employee profiles")
        return True

if __name__ == '__main__':
    print("\n🚀 Starting Profile Names Migration...\n")
    
    # Step 1: Create missing employee profiles
    success = migrate_profile_names()
    
    if not success:
        print("\n❌ Migration encountered errors. Please review above.")
        sys.exit(1)
    
    # Step 2: Verify migration
    verify_success = verify_migration()
    
    if not verify_success:
        print("\n❌ Verification failed. Please check the migration results.")
        sys.exit(1)
    
    # Step 3: Sync names
    sync_success = sync_user_names_with_employee()
    
    if sync_success:
        print("\n" + "=" * 70)
        print("✅ ALL MIGRATION STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Review the migrated data")
        print("2. Update employee profiles with complete information (NRIC, position, etc.)")
        print("3. Update all templates to use employee_profile names")
        print("4. Update routes to use get_first_name and get_last_name properties")
        print("5. Eventually drop first_name and last_name from hrm_users table")
        print("\nFor now, both hrm_users and hrm_employee have the same names,")
        print("ensuring backward compatibility during the transition.")
        print("=" * 70 + "\n")
    else:
        print("\n❌ Sync failed.")
        sys.exit(1)