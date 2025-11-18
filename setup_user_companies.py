#!/usr/bin/env python
"""
Interactive script to add multiple companies to users
Run this to easily manage user-company relationships
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Company, UserCompanyAccess
from datetime import datetime


def show_users():
    """Display all users"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database")
            return None
        
        print("\n" + "="*80)
        print("👥 AVAILABLE USERS")
        print("="*80)
        print(f"{'ID':<5} {'Username':<20} {'Role':<20} {'Companies':<20}")
        print("-"*80)
        
        for user in users:
            role_name = user.role.name if user.role else "No Role"
            company_count = len(user.company_access)
            print(f"{user.id:<5} {user.username:<20} {role_name:<20} {company_count}")
        
        print("="*80)
        return users


def show_companies():
    """Display all companies"""
    with app.app_context():
        companies = Company.query.all()
        
        if not companies:
            print("❌ No companies found in database")
            return None
        
        print("\n" + "="*80)
        print("🏢 AVAILABLE COMPANIES")
        print("="*80)
        print(f"{'ID':<40} {'Name':<30} {'Users':<10}")
        print("-"*80)
        
        for company in companies:
            user_count = UserCompanyAccess.query.filter_by(company_id=company.id).count()
            company_id_short = str(company.id)[:20] + "..."
            print(f"{company_id_short:<40} {company.name:<30} {user_count:<10}")
        
        print("="*80)
        return companies


def show_user_companies(user_id):
    """Show all companies for a specific user"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"\n❌ User {user_id} not found")
            return
        
        print(f"\n📋 Companies for user: {user.username}")
        print("-"*60)
        
        if not user.company_access:
            print("No companies assigned")
        else:
            for i, access in enumerate(user.company_access, 1):
                company = access.company
                print(f"{i}. {company.name}")
                print(f"   └─ Assigned: {access.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("-"*60)
        print(f"Total: {len(user.company_access)} company(ies)\n")


def add_company_to_user_interactive():
    """Interactive: Add company to user"""
    with app.app_context():
        print("\n" + "="*80)
        print("➕ ADD COMPANY TO USER")
        print("="*80)
        
        # Get user
        users = User.query.all()
        if not users:
            print("❌ No users available")
            return
        
        print("\nSelect User:")
        for i, user in enumerate(users, 1):
            role = user.role.name if user.role else "No Role"
            print(f"  {i}. {user.username} ({role})")
        
        try:
            user_choice = int(input("\nEnter user number: ")) - 1
            if user_choice < 0 or user_choice >= len(users):
                print("❌ Invalid selection")
                return
            user = users[user_choice]
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Get companies
        companies = Company.query.all()
        if not companies:
            print("❌ No companies available")
            return
        
        # Show user's current companies
        current_company_ids = {access.company_id for access in user.company_access}
        
        print(f"\nSelect Company(ies) for {user.username}:")
        available_companies = [c for c in companies if c.id not in current_company_ids]
        
        if not available_companies:
            print(f"✅ User already has access to all companies")
            return
        
        for i, company in enumerate(available_companies, 1):
            print(f"  {i}. {company.name}")
        
        try:
            companies_input = input("\nEnter company numbers (comma-separated): ").strip()
            if not companies_input:
                print("❌ No companies selected")
                return
            
            choices = [int(x.strip()) - 1 for x in companies_input.split(',')]
            selected_companies = []
            
            for choice in choices:
                if choice < 0 or choice >= len(available_companies):
                    print(f"⚠️  Invalid selection: {choice + 1}")
                    continue
                selected_companies.append(available_companies[choice])
        except ValueError:
            print("❌ Invalid input")
            return
        
        if not selected_companies:
            print("❌ No valid companies selected")
            return
        
        # Add companies
        added_count = 0
        for company in selected_companies:
            try:
                access = UserCompanyAccess(
                    user_id=user.id,
                    company_id=company.id
                )
                db.session.add(access)
                added_count += 1
                print(f"✓ {company.name}")
            except Exception as e:
                print(f"✗ {company.name}: {str(e)}")
        
        try:
            db.session.commit()
            print(f"\n✅ Successfully added {added_count} company(ies) to {user.username}")
            show_user_companies(user.id)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saving changes: {str(e)}")


def remove_company_from_user_interactive():
    """Interactive: Remove company from user"""
    with app.app_context():
        print("\n" + "="*80)
        print("❌ REMOVE COMPANY FROM USER")
        print("="*80)
        
        # Get users with company access
        users_with_access = User.query.join(UserCompanyAccess).distinct().all()
        
        if not users_with_access:
            print("❌ No users with company access found")
            return
        
        print("\nSelect User:")
        for i, user in enumerate(users_with_access, 1):
            company_count = len(user.company_access)
            print(f"  {i}. {user.username} ({company_count} companies)")
        
        try:
            user_choice = int(input("\nEnter user number: ")) - 1
            if user_choice < 0 or user_choice >= len(users_with_access):
                print("❌ Invalid selection")
                return
            user = users_with_access[user_choice]
        except ValueError:
            print("❌ Invalid input")
            return
        
        if not user.company_access:
            print(f"ℹ️  {user.username} has no companies assigned")
            return
        
        print(f"\nSelect Company to remove:")
        for i, access in enumerate(user.company_access, 1):
            print(f"  {i}. {access.company.name}")
        
        try:
            company_choice = int(input("\nEnter company number: ")) - 1
            if company_choice < 0 or company_choice >= len(user.company_access):
                print("❌ Invalid selection")
                return
            access_to_remove = user.company_access[company_choice]
        except ValueError:
            print("❌ Invalid input")
            return
        
        confirm = input(f"\nRemove '{access_to_remove.company.name}' from '{user.username}'? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return
        
        try:
            db.session.delete(access_to_remove)
            db.session.commit()
            print(f"✅ Successfully removed '{access_to_remove.company.name}' from '{user.username}'")
            show_user_companies(user.id)
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")


def bulk_add_companies():
    """Bulk add: All HR Managers and Tenant Admins get access to all companies"""
    with app.app_context():
        print("\n" + "="*80)
        print("📊 BULK ADD - All roles get all companies")
        print("="*80)
        
        users = User.query.all()
        companies = Company.query.all()
        
        if not users or not companies:
            print("❌ Need at least one user and one company")
            return
        
        print(f"\nThis will add {len(companies)} companies to {len(users)} users")
        print("(Existing relationships will be skipped)")
        
        confirm = input("\nContinue? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return
        
        added_count = 0
        skipped_count = 0
        
        for user in users:
            for company in companies:
                existing = UserCompanyAccess.query.filter_by(
                    user_id=user.id,
                    company_id=company.id
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                try:
                    access = UserCompanyAccess(
                        user_id=user.id,
                        company_id=company.id
                    )
                    db.session.add(access)
                    added_count += 1
                except Exception as e:
                    print(f"⚠️  Error for {user.username}/{company.name}: {str(e)}")
        
        try:
            db.session.commit()
            print(f"\n✅ Bulk add complete!")
            print(f"  ✓ Added: {added_count}")
            print(f"  ⊘ Skipped (already exist): {skipped_count}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")


def generate_summary():
    """Show summary statistics"""
    with app.app_context():
        print("\n" + "="*80)
        print("📊 SUMMARY STATISTICS")
        print("="*80)
        
        total_users = User.query.count()
        total_companies = Company.query.count()
        total_accesses = UserCompanyAccess.query.count()
        
        print(f"Total Users:              {total_users}")
        print(f"Total Companies:          {total_companies}")
        print(f"Total Relationships:      {total_accesses}")
        
        if total_users > 0 and total_companies > 0:
            max_possible = total_users * total_companies
            coverage = (total_accesses / max_possible * 100) if max_possible > 0 else 0
            print(f"Coverage:                 {coverage:.1f}%")
        
        # Users with no company access
        users_no_access = User.query.outerjoin(UserCompanyAccess).filter(
            UserCompanyAccess.id == None
        ).count()
        print(f"\nUsers with NO company:    {users_no_access}")
        
        # Users with multiple companies
        users_multi = db.session.query(
            db.func.count(UserCompanyAccess.user_id)
        ).group_by(UserCompanyAccess.user_id).filter(
            db.func.count(UserCompanyAccess.user_id) > 1
        ).count()
        print(f"Users with MULTIPLE:      {users_multi}")
        
        print("="*80 + "\n")


def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("🎯 USER-COMPANY MANAGEMENT")
        print("="*80)
        print("1. View all users")
        print("2. View all companies")
        print("3. View companies for a user")
        print("4. Add company to user")
        print("5. Remove company from user")
        print("6. Bulk add (all companies to all users)")
        print("7. Summary statistics")
        print("8. Exit")
        print("="*80)
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == '1':
            show_users()
        elif choice == '2':
            show_companies()
        elif choice == '3':
            with app.app_context():
                try:
                    user_id = int(input("Enter user ID: "))
                    show_user_companies(user_id)
                except ValueError:
                    print("❌ Invalid input")
        elif choice == '4':
            add_company_to_user_interactive()
        elif choice == '5':
            remove_company_from_user_interactive()
        elif choice == '6':
            bulk_add_companies()
        elif choice == '7':
            generate_summary()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)