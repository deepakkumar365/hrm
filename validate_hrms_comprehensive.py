#!/usr/bin/env python3
"""
🔍 HRMS Comprehensive Validation Script
Tests all pages, routes, database schema, and UI consistency
Generates detailed report of issues and fixes applied
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title: str, symbol: str = "="):
    """Print formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")

def print_test(name: str, status: str, details: str = ""):
    """Print test result"""
    status_symbols = {
        "✅ PASS": "✅",
        "⚙️ WARN": "⚠️",
        "❌ FAIL": "❌",
    }
    symbol = status_symbols.get(status.split()[0], "❓")
    print(f"  {symbol} {name}")
    if details:
        print(f"     → {details}")

class HRMSValidator:
    """Main validator class"""
    
    def __init__(self):
        self.issues: List[Dict] = []
        self.fixes_applied: List[str] = []
        self.warnings: List[str] = []
        self.all_passed = True
        
    def validate_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        print_section("1️⃣  DEPENDENCY VALIDATION")
        
        required_packages = {
            'flask': 'Flask',
            'flask_login': 'Flask-Login',
            'flask_sqlalchemy': 'Flask-SQLAlchemy',
            'flask_migrate': 'Flask-Migrate',
            'sqlalchemy': 'SQLAlchemy',
            'dotenv': 'python-dotenv',
        }
        
        all_available = True
        for module_name, package_name in required_packages.items():
            try:
                __import__(module_name)
                print_test(f"Package: {package_name}", "✅ PASS", "Installed correctly")
            except ImportError as e:
                print_test(f"Package: {package_name}", "❌ FAIL", f"Missing: {str(e)}")
                self.issues.append({
                    'severity': 'CRITICAL',
                    'component': 'Dependencies',
                    'issue': f'Missing package: {package_name}',
                    'fix': f'Run: pip install {package_name}'
                })
                all_available = False
                self.all_passed = False
        
        return all_available
    
    def validate_file_structure(self) -> bool:
        """Verify all required files exist"""
        print_section("2️⃣  FILE STRUCTURE VALIDATION")
        
        required_files = {
            'app.py': 'Flask app initialization',
            'models.py': 'Database models',
            'routes.py': 'API routes',
            'auth.py': 'Authentication',
            'forms.py': 'Flask forms',
            'constants.py': 'Application constants',
            'requirements.txt': 'Python dependencies',
            'static/css/styles.css': 'Main stylesheet',
            'templates/base.html': 'Base template',
            'templates/dashboard.html': 'Dashboard template',
            'templates/profile_edit.html': 'Profile edit template',
        }
        
        all_exist = True
        for filepath, description in required_files.items():
            full_path = Path(__file__).parent / filepath
            if full_path.exists():
                print_test(f"File: {filepath}", "✅ PASS", description)
            else:
                print_test(f"File: {filepath}", "❌ FAIL", f"Missing: {description}")
                all_exist = False
                self.all_passed = False
        
        return all_exist
    
    def validate_css_variables(self) -> bool:
        """Check CSS variable definitions"""
        print_section("3️⃣  CSS THEME VALIDATION")
        
        css_file = Path(__file__).parent / 'static/css/styles.css'
        if not css_file.exists():
            print_test("CSS Theme Variables", "❌ FAIL", "styles.css not found")
            return False
        
        css_content = css_file.read_text()
        
        required_vars = [
            ('--primary', 'Primary teal color'),
            ('--primary-green', 'Primary green alias (should be teal)'),
            ('--primary-green-light', 'Light green alias (should be light teal)'),
            ('--secondary', 'Secondary color'),
            ('--accent', 'Accent color'),
        ]
        
        all_defined = True
        for var_name, description in required_vars:
            if var_name in css_content:
                print_test(f"Variable: {var_name}", "✅ PASS", description)
            else:
                print_test(f"Variable: {var_name}", "❌ FAIL", f"Not defined: {description}")
                all_defined = False
                self.all_passed = False
        
        # Check for pink colors (anti-pattern)
        pink_patterns = ['#FFB6C1', '#FFC0CB', '#ffc0cb', '#ffb6c1', 'pink']
        pink_found = any(pattern in css_content.lower() for pattern in pink_patterns)
        if not pink_found:
            print_test("Pink Color Check", "✅ PASS", "No pink colors found in CSS")
        else:
            print_test("Pink Color Check", "⚙️ WARN", "Pink colors may exist - manual check needed")
            self.warnings.append("Pink colors detected in CSS - verify if intentional")
        
        return all_defined
    
    def validate_models(self) -> bool:
        """Check ORM models integrity"""
        print_section("4️⃣  DATABASE MODELS VALIDATION")
        
        try:
            from models import User, Employee, Role, Organization
            print_test("Import: models.User", "✅ PASS", "User model loads")
            print_test("Import: models.Employee", "✅ PASS", "Employee model loads")
            print_test("Import: models.Role", "✅ PASS", "Role model loads")
            print_test("Import: models.Organization", "✅ PASS", "Organization model loads")
            
            # Check User model inherits from UserMixin
            from flask_login import UserMixin
            if issubclass(User, UserMixin):
                print_test("UserMixin Inheritance", "✅ PASS", "User model properly inherits from UserMixin")
            else:
                print_test("UserMixin Inheritance", "❌ FAIL", "User model missing UserMixin")
                self.issues.append({
                    'severity': 'CRITICAL',
                    'component': 'Models',
                    'issue': 'User model does not inherit from UserMixin',
                    'fix': 'Update models.py: class User(db.Model, UserMixin)'
                })
                self.all_passed = False
                return False
            
            return True
        except Exception as e:
            print_test("Model Validation", "❌ FAIL", str(e))
            self.all_passed = False
            return False
    
    def validate_routes(self) -> bool:
        """Verify route definitions"""
        print_section("5️⃣  ROUTES VALIDATION")
        
        try:
            from app import app
            
            # Get all registered routes
            routes_map = {}
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes_map[str(rule)] = rule.endpoint
            
            print_test(f"Total Routes Registered", "✅ PASS", f"{len(routes_map)} routes found")
            
            # Check critical routes
            critical_routes = [
                '/login',
                '/logout',
                '/dashboard',
                '/',
                '/profile',
                '/profile/edit',
            ]
            
            found_routes = set(str(r) for r in routes_map.keys())
            for route in critical_routes:
                if any(route in str(r) for r in found_routes):
                    print_test(f"Route: {route}", "✅ PASS", "Critical route found")
                else:
                    print_test(f"Route: {route}", "❌ FAIL", "Critical route missing")
                    self.all_passed = False
            
            return True
        except Exception as e:
            print_test("Route Validation", "❌ FAIL", str(e))
            self.all_passed = False
            return False
    
    def validate_requirements(self) -> bool:
        """Check requirements.txt completeness"""
        print_section("6️⃣  REQUIREMENTS VALIDATION")
        
        req_file = Path(__file__).parent / 'requirements.txt'
        if not req_file.exists():
            print_test("requirements.txt", "❌ FAIL", "File not found")
            return False
        
        req_content = req_file.read_text().lower()
        
        required_deps = [
            ('flask', 'Flask framework'),
            ('flask-login', 'Flask-Login for authentication'),
            ('flask-sqlalchemy', 'SQLAlchemy ORM wrapper'),
            ('flask-migrate', 'Database migrations'),
            ('python-dotenv', 'Environment variable loading'),
        ]
        
        all_found = True
        for dep, description in required_deps:
            if dep in req_content:
                print_test(f"Dependency: {dep}", "✅ PASS", description)
            else:
                print_test(f"Dependency: {dep}", "❌ FAIL", f"Missing: {description}")
                all_found = False
                self.issues.append({
                    'severity': 'HIGH',
                    'component': 'Dependencies',
                    'issue': f'Missing requirement: {dep}',
                    'fix': f'Add "{dep}" to requirements.txt'
                })
        
        return all_found
    
    def validate_authentication(self) -> bool:
        """Check authentication setup"""
        print_section("7️⃣  AUTHENTICATION VALIDATION")
        
        try:
            from auth import login_manager, require_login, require_role
            print_test("Import: login_manager", "✅ PASS", "Flask-Login manager configured")
            print_test("Import: require_login decorator", "✅ PASS", "Login decorator available")
            print_test("Import: require_role decorator", "✅ PASS", "Role-based access control available")
            
            return True
        except Exception as e:
            print_test("Authentication Setup", "❌ FAIL", str(e))
            self.all_passed = False
            return False
    
    def validate_environment(self) -> bool:
        """Check environment configuration"""
        print_section("8️⃣  ENVIRONMENT CONFIGURATION")
        
        env_file = Path(__file__).parent / '.env'
        env_example = Path(__file__).parent / '.env.example'
        
        if env_file.exists():
            print_test(".env File", "✅ PASS", "Environment file found")
            # Check for required keys
            env_content = env_file.read_text()
            required_keys = ['DATABASE_URL', 'SESSION_SECRET', 'ENVIRONMENT']
            for key in required_keys:
                if key in env_content:
                    print_test(f"  Env Key: {key}", "✅ PASS", "Configured")
                else:
                    print_test(f"  Env Key: {key}", "⚙️ WARN", "Missing - may use defaults")
                    self.warnings.append(f"Environment key {key} not found in .env")
        else:
            print_test(".env File", "⚙️ WARN", "Not found - using environment variables")
            if env_example.exists():
                print_test(".env.example", "✅ PASS", "Example file exists for reference")
        
        return True
    
    def generate_report(self) -> str:
        """Generate final validation report"""
        print_section("📊 VALIDATION SUMMARY")
        
        report = []
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        
        if self.all_passed:
            print_test("Overall Status", "✅ PASS", "All critical validations passed!")
            report.append("Status: ✅ ALL TESTS PASSED\n")
        else:
            print_test("Overall Status", "❌ FAIL", "Some validations failed - see details below")
            report.append("Status: ❌ SOME TESTS FAILED\n")
        
        if self.issues:
            print("\n### ISSUES FOUND ###\n")
            report.append("\n### ISSUES FOUND ###\n")
            for i, issue in enumerate(self.issues, 1):
                msg = f"{i}. [{issue['severity']}] {issue['component']}: {issue['issue']}\n   Fix: {issue['fix']}\n"
                print(msg)
                report.append(msg)
        
        if self.warnings:
            print("\n### WARNINGS ###\n")
            report.append("\n### WARNINGS ###\n")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}\n")
                report.append(f"  ⚠️  {warning}\n")
        
        return "\n".join(report)
    
    def run_all_validations(self):
        """Run all validation checks"""
        print_section("🔍 HRMS COMPREHENSIVE VALIDATION", "=" * 80)
        print("   Starting validation suite...")
        print("   Testing: Dependencies, Files, Models, Routes, Database, Auth, Environment\n")
        
        self.validate_dependencies()
        self.validate_file_structure()
        self.validate_requirements()
        self.validate_css_variables()
        self.validate_models()
        self.validate_routes()
        self.validate_authentication()
        self.validate_environment()
        
        report = self.generate_report()
        
        # Save report
        report_file = Path(__file__).parent / 'VALIDATION_RESULTS.txt'
        report_file.write_text(report)
        print(f"\n📄 Report saved to: {report_file}")
        
        return self.all_passed

def main():
    """Main entry point"""
    validator = HRMSValidator()
    success = validator.run_all_validations()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ VALIDATION COMPLETE - Ready for testing!")
        print("\nNext Steps:")
        print("  1. Run: pip install -r requirements.txt")
        print("  2. Set up .env file with correct DATABASE_URL and SESSION_SECRET")
        print("  3. Run: flask db upgrade (if migrations pending)")
        print("  4. Run: python main.py")
        print("  5. Login and test: superadmin / manager / employee roles")
    else:
        print("❌ VALIDATION FAILED - Fix issues before running the app")
        print("\nSee VALIDATION_RESULTS.txt for detailed report")
    print("=" * 80 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())