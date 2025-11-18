#!/usr/bin/env python
"""
Data migration script to populate UserCompanyAccess table with existing user-company relationships.
This script should be run after the database migration for multi-company support.

Usage: python migrate_user_company_access.py
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Employee, Company, UserCompanyAccess
from sqlalchemy import and_


def migrate_existing_user_companies():
    """Migrate existing user-company relationships from Employee table to UserCompanyAccess"""
    
    with app.app_context():
        print("🔄 Starting User-Company Access Migration...")
        print("-" * 60)
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            # Get all users with HR Manager or Tenant Admin role
            hr_managers = User.query.filter(
                User.role.has(db.and_(
                    db.func.lower(db.Column(db.String)) == 'hr manager' or 
                    db.func.lower(db.Column(db.String)) == 'tenant admin'
                ))
            ).all()
            
            # Alternative approach: Get all users and filter in Python
            all_users = User.query.all()
            
            for user in all_users:
                try:
                    role_name = user.role.name if user.role else None
                    
                    # Skip if user doesn't have a role
                    if not role_name:
                        print(f"⚠️  User {user.username} (ID: {user.id}) - No role assigned")
                        skipped_count += 1
                        continue
                    
                    # Super Admin users get access to all companies
                    if role_name == 'Super Admin':
                        companies = Company.query.all()
                        for company in companies:
                            # Check if access already exists
                            existing = UserCompanyAccess.query.filter_by(
                                user_id=user.id,
                                company_id=company.id
                            ).first()
                            
                            if not existing:
                                access = UserCompanyAccess(
                                    user_id=user.id,
                                    company_id=company.id
                                )
                                db.session.add(access)
                                migrated_count += 1
                        
                        if companies:
                            print(f"✓ Super Admin '{user.username}' - Added access to {len(companies)} company(ies)")
                    
                    # HR Manager and Tenant Admin get access to their employee's company
                    elif role_name in ['HR Manager', 'Tenant Admin']:
                        if user.employee_profile and user.employee_profile.company:
                            company_id = user.employee_profile.company_id
                            
                            # Check if access already exists
                            existing = UserCompanyAccess.query.filter_by(
                                user_id=user.id,
                                company_id=company_id
                            ).first()
                            
                            if not existing:
                                access = UserCompanyAccess(
                                    user_id=user.id,
                                    company_id=company_id
                                )
                                db.session.add(access)
                                migrated_count += 1
                                print(f"✓ {role_name} '{user.username}' - Added access to company {user.employee_profile.company.name}")
                            else:
                                print(f"⊘ {role_name} '{user.username}' - Access already exists for {user.employee_profile.company.name}")
                                skipped_count += 1
                        else:
                            print(f"⚠️  {role_name} '{user.username}' - No employee profile or company assigned")
                            skipped_count += 1
                    else:
                        print(f"⊘ {role_name} '{user.username}' - No company access needed for this role")
                        skipped_count += 1
                
                except Exception as e:
                    print(f"✗ Error processing user {user.username}: {str(e)}")
                    error_count += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            print("-" * 60)
            print(f"✓ Migration Complete!")
            print(f"  - Migrated: {migrated_count} user-company access records")
            print(f"  - Skipped: {skipped_count} (already exist or not applicable)")
            print(f"  - Errors: {error_count}")
            print(f"\n✓ Total users processed: {len(all_users)}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed with error: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = migrate_existing_user_companies()
    sys.exit(0 if success else 1)