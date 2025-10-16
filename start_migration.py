"""
Migration Starter Script
This script helps you get started with the role table migration
"""
import os
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def print_section(title):
    """Print a section title"""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)

def main():
    print_header("ROLE TABLE MIGRATION - GETTING STARTED")
    
    print("Welcome to the Role Table Migration wizard!")
    print("This script will help you prepare for and execute the migration.")
    print("\nMigration: role table → hrm_roles table")
    
    # Step 1: Documentation
    print_section("STEP 1: Review Documentation")
    print("\nAvailable documentation files:")
    print("  1. MIGRATION_VISUAL_GUIDE.md  - Visual overview (START HERE)")
    print("  2. MIGRATION_SUMMARY.md       - Quick summary")
    print("  3. ROLE_MIGRATION_README.md   - Detailed guide")
    print("  4. MIGRATION_CHECKLIST.md     - Step-by-step checklist")
    
    response = input("\nHave you reviewed the documentation? (yes/no): ")
    if response.lower() != 'yes':
        print("\n⚠️  Please review the documentation first!")
        print("   Start with: MIGRATION_VISUAL_GUIDE.md")
        print("   Then read: MIGRATION_SUMMARY.md")
        sys.exit(0)
    
    # Step 2: Prerequisites
    print_section("STEP 2: Check Prerequisites")
    print("\nBefore proceeding, ensure you have:")
    print("  ✓ Database admin access")
    print("  ✓ Ability to stop the application")
    print("  ✓ Ability to create database backups")
    print("  ✓ Python environment activated")
    
    response = input("\nDo you have all prerequisites? (yes/no): ")
    if response.lower() != 'yes':
        print("\n⚠️  Please ensure all prerequisites are met first!")
        sys.exit(0)
    
    # Step 3: Install Dependencies
    print_section("STEP 3: Install Dependencies")
    print("\nThe migration scripts require the 'tabulate' package.")
    
    response = input("\nInstall dependencies now? (yes/no): ")
    if response.lower() == 'yes':
        print("\nInstalling dependencies...")
        os.system('python install_migration_deps.py')
    else:
        print("\n⚠️  You can install later with: python install_migration_deps.py")
    
    # Step 4: Check Current State
    print_section("STEP 4: Check Current State")
    print("\nLet's check the current state of your database.")
    
    response = input("\nRun verification script now? (yes/no): ")
    if response.lower() == 'yes':
        print("\nRunning verification...")
        os.system('python verify_role_migration.py')
        input("\nPress Enter to continue...")
    
    # Step 5: Backup Reminder
    print_section("STEP 5: Database Backup")
    print("\n⚠️  CRITICAL: You MUST create a database backup before proceeding!")
    print("\nBackup command:")
    print("  pg_dump -U your_username -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql")
    print("\nOr on Windows:")
    print("  pg_dump -U your_username -d your_database > backup.sql")
    
    response = input("\nHave you created a database backup? (yes/no): ")
    if response.lower() != 'yes':
        print("\n⚠️  Please create a database backup first!")
        print("   This is CRITICAL for safety!")
        sys.exit(0)
    
    # Step 6: Stop Application
    print_section("STEP 6: Stop Application")
    print("\nYou need to stop the Flask application before migration.")
    print("This prevents data inconsistencies during the migration.")
    
    response = input("\nHave you stopped the application? (yes/no): ")
    if response.lower() != 'yes':
        print("\n⚠️  Please stop the application first!")
        sys.exit(0)
    
    # Step 7: Ready to Migrate
    print_section("STEP 7: Ready to Migrate")
    print("\n✅ All prerequisites are met!")
    print("✅ Documentation reviewed")
    print("✅ Dependencies installed")
    print("✅ Database backed up")
    print("✅ Application stopped")
    
    print("\n" + "=" * 70)
    print("MIGRATION OPTIONS")
    print("=" * 70)
    print("\nYou have three options to run the migration:")
    print("\n1. Standalone Script (RECOMMENDED)")
    print("   - Interactive with safety checks")
    print("   - Command: python migrate_roles_table.py")
    print("\n2. Alembic Migration")
    print("   - Automated with version control")
    print("   - Command: flask db upgrade")
    print("\n3. Direct SQL")
    print("   - For database administrators")
    print("   - Command: psql -U user -d db < migrations/versions/005_migrate_role_to_hrm_roles.sql")
    
    print("\n" + "=" * 70)
    response = input("\nRun migration now using standalone script? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\n" + "=" * 70)
        print("STARTING MIGRATION")
        print("=" * 70)
        print("\nLaunching migration script...")
        print("Follow the prompts carefully.\n")
        input("Press Enter to start...")
        
        os.system('python migrate_roles_table.py')
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETED")
        print("=" * 70)
        
        response = input("\nRun verification script? (yes/no): ")
        if response.lower() == 'yes':
            os.system('python verify_role_migration.py')
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\n1. Review verification results above")
        print("2. Start your Flask application")
        print("3. Test login and role functionality")
        print("4. Monitor logs for any issues")
        print("5. Keep backup for at least 30 days")
        
        print("\n✅ Migration process complete!")
        print("   Thank you for using the migration wizard.\n")
    else:
        print("\n" + "=" * 70)
        print("MANUAL MIGRATION")
        print("=" * 70)
        print("\nYou chose to run the migration manually.")
        print("\nRun one of these commands:")
        print("  python migrate_roles_table.py")
        print("  flask db upgrade")
        print("  psql -U user -d db < migrations/versions/005_migrate_role_to_hrm_roles.sql")
        
        print("\nAfter migration, run:")
        print("  python verify_role_migration.py")
        
        print("\nGood luck with your migration!\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration wizard cancelled by user.")
        print("   You can restart anytime with: python start_migration.py\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)