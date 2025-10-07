"""
Quick Setup Script for Tenant-Company Hierarchy
This script helps integrate the new tenant/company features into your existing HRMS
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_files_exist():
    """Check if all required files were created"""
    print_header("STEP 1: Checking Required Files")
    
    required_files = [
        'migrations/versions/001_add_tenant_company_hierarchy.sql',
        'migrations/versions/002_test_data_tenant_company.sql',
        'routes_tenant_company.py',
        'run_tenant_company_migration.py',
        'templates/masters/tenants.html',
        'templates/masters/companies.html',
        'TENANT_COMPANY_MIGRATION_GUIDE.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_models_updated():
    """Check if models.py has been updated"""
    print_header("STEP 2: Checking Models")
    
    models_file = Path(__file__).parent / 'models.py'
    
    if not models_file.exists():
        print("❌ models.py not found")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Tenant model': 'class Tenant(db.Model):',
        'Company model': 'class Company(db.Model):',
        'UUID import': 'from sqlalchemy.dialects.postgresql import UUID',
        'Employee.company_id': 'company_id = db.Column(UUID',
        'Organization.tenant_id': 'tenant_id = db.Column(UUID'
    }
    
    all_good = True
    for check_name, check_string in checks.items():
        if check_string in content:
            print(f"✅ {check_name} found")
        else:
            print(f"❌ {check_name} NOT found")
            all_good = False
    
    return all_good


def show_integration_steps():
    """Show steps to integrate the new features"""
    print_header("STEP 3: Integration Instructions")
    
    print("To complete the integration, follow these steps:\n")
    
    print("1️⃣  Import the new routes in your main application file:")
    print("    In main.py or app.py, add:")
    print("    " + "-" * 60)
    print("    import routes_tenant_company")
    print("    " + "-" * 60)
    print()
    
    print("2️⃣  Run the database migration:")
    print("    " + "-" * 60)
    print("    python run_tenant_company_migration.py")
    print("    " + "-" * 60)
    print()
    
    print("3️⃣  Update your navigation menu (optional):")
    print("    Add links to tenant/company management pages:")
    print("    " + "-" * 60)
    print("    <a href=\"{{ url_for('tenants_page') }}\">Tenants</a>")
    print("    <a href=\"{{ url_for('companies_page') }}\">Companies</a>")
    print("    " + "-" * 60)
    print()
    
    print("4️⃣  Restart your Flask application:")
    print("    " + "-" * 60)
    print("    # Development")
    print("    python main.py")
    print()
    print("    # Production (Gunicorn)")
    print("    pkill gunicorn")
    print("    gunicorn -c gunicorn.conf.py main:app")
    print("    " + "-" * 60)
    print()


def show_api_examples():
    """Show example API calls"""
    print_header("STEP 4: Testing API Endpoints")
    
    print("Once the migration is complete, test these endpoints:\n")
    
    print("📋 List all tenants:")
    print("   GET /api/tenants")
    print()
    
    print("➕ Create a tenant:")
    print("   POST /api/tenants")
    print("   Body: {\"name\": \"My Tenant\", \"code\": \"MYTENANT\"}")
    print()
    
    print("📋 List all companies:")
    print("   GET /api/companies")
    print()
    
    print("➕ Create a company:")
    print("   POST /api/companies")
    print("   Body: {\"tenant_id\": \"<uuid>\", \"name\": \"My Company\", \"code\": \"MYCO\"}")
    print()
    
    print("🔗 Link employee to company:")
    print("   PUT /api/employees/<id>/link-company")
    print("   Body: {\"company_id\": \"<uuid>\"}")
    print()


def show_next_steps():
    """Show recommended next steps"""
    print_header("STEP 5: Recommended Next Steps")
    
    print("After successful integration:\n")
    
    print("1. 📖 Read the full migration guide:")
    print("   TENANT_COMPANY_MIGRATION_GUIDE.md")
    print()
    
    print("2. 🧪 Test the new features:")
    print("   - Create a tenant via API or UI")
    print("   - Create companies under the tenant")
    print("   - Link existing employees to companies")
    print()
    
    print("3. 🎨 Customize the UI templates:")
    print("   - templates/masters/tenants.html")
    print("   - templates/masters/companies.html")
    print()
    
    print("4. 🔒 Review security settings:")
    print("   - Ensure role-based access is properly configured")
    print("   - Test cascading deletes in a safe environment")
    print()
    
    print("5. 📊 Plan data migration:")
    print("   - Decide how to organize existing employees into companies")
    print("   - Create a data migration script if needed")
    print()


def main():
    """Main setup check"""
    print("\n" + "🏢" * 35)
    print("  TENANT-COMPANY HIERARCHY SETUP VERIFICATION")
    print("🏢" * 35)
    
    # Check files
    files_ok = check_files_exist()
    
    # Check models
    models_ok = check_models_updated()
    
    # Show integration steps
    show_integration_steps()
    
    # Show API examples
    show_api_examples()
    
    # Show next steps
    show_next_steps()
    
    # Final summary
    print_header("SETUP VERIFICATION SUMMARY")
    
    if files_ok and models_ok:
        print("✅ All files created successfully")
        print("✅ Models updated correctly")
        print()
        print("🎉 You're ready to run the migration!")
        print()
        print("Next command to run:")
        print("   python run_tenant_company_migration.py")
    else:
        print("⚠️  Some issues were found. Please review the output above.")
        print()
        if not files_ok:
            print("❌ Some required files are missing")
        if not models_ok:
            print("❌ Models.py needs to be updated")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()