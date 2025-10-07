"""
Check if all required dependencies are installed for tenant-company hierarchy
"""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False


def main():
    print("\n" + "=" * 70)
    print("  DEPENDENCY CHECK FOR TENANT-COMPANY HIERARCHY")
    print("=" * 70 + "\n")
    
    print("Checking required Python packages...\n")
    
    required = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_login': 'Flask-Login',
        'flask_migrate': 'Flask-Migrate',
        'sqlalchemy': 'SQLAlchemy',
        'psycopg2': 'psycopg2-binary',
        'dotenv': 'python-dotenv',
        'werkzeug': 'Werkzeug',
    }
    
    all_installed = True
    for module, package in required.items():
        if not check_import(module, package):
            all_installed = False
    
    print("\n" + "=" * 70)
    
    if all_installed:
        print("✅ All required dependencies are installed!")
        print("\nYou're ready to run the migration:")
        print("   python run_tenant_company_migration.py")
    else:
        print("❌ Some dependencies are missing.")
        print("\nInstall missing packages with:")
        print("   pip install -r requirements.txt")
        print("\nOr install individually:")
        print("   pip install Flask Flask-SQLAlchemy Flask-Login Flask-Migrate")
        print("   pip install psycopg2-binary python-dotenv")
    
    print("=" * 70 + "\n")
    
    return 0 if all_installed else 1


if __name__ == '__main__':
    sys.exit(main())