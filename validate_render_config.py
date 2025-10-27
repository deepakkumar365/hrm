#!/usr/bin/env python3
"""
Validate Render Configuration
Checks render.yaml and environment variables before deployment
"""

import os
import sys
import yaml
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RenderConfigValidator:
    def __init__(self):
        self.render_yaml_path = 'render.yaml'
        self.render_config = None
        self.errors = []
        self.warnings = []
        self.info = []
        
    def load_render_yaml(self):
        """Load and parse render.yaml"""
        try:
            with open(self.render_yaml_path, 'r') as f:
                self.render_config = yaml.safe_load(f)
            self.info.append("✅ render.yaml loaded successfully")
            return True
        except FileNotFoundError:
            self.errors.append("❌ render.yaml not found in project root")
            return False
        except yaml.YAMLError as e:
            self.errors.append(f"❌ render.yaml is invalid YAML: {e}")
            return False
    
    def validate_services(self):
        """Validate services configuration"""
        print("🔍 Validating Services Configuration...")
        
        if 'services' not in self.render_config:
            self.errors.append("❌ 'services' section missing in render.yaml")
            return False
        
        services = self.render_config['services']
        if not services:
            self.errors.append("❌ 'services' section is empty")
            return False
        
        web_service = None
        for service in services:
            if service.get('type') == 'web':
                web_service = service
                break
        
        if not web_service:
            self.errors.append("❌ No web service found in render.yaml")
            return False
        
        # Validate service configuration
        checks = {
            'name': 'Service name',
            'env': 'Environment type',
            'buildCommand': 'Build command',
            'startCommand': 'Start command',
            'healthCheckPath': 'Health check path',
        }
        
        for key, description in checks.items():
            if key not in web_service:
                self.warnings.append(f"⚠️  {description} ({key}) not configured")
            else:
                value = web_service[key]
                if value:
                    self.info.append(f"✅ {description}: {value}")
                else:
                    self.errors.append(f"❌ {description} ({key}) is empty")
        
        # Validate environment variables
        self.validate_env_vars(web_service)
        
        return len(self.errors) == 0
    
    def validate_env_vars(self, service):
        """Validate environment variables configuration"""
        print("\n🔐 Validating Environment Variables...")
        
        if 'envVars' not in service:
            self.errors.append("❌ 'envVars' section missing in web service")
            return False
        
        env_vars = service['envVars']
        required_vars = {
            'PROD_DATABASE_URL': 'Production database connection string',
            'PROD_SESSION_SECRET': 'Production session secret',
            'ENVIRONMENT': 'Environment type (should be "production")',
            'PYTHON_VERSION': 'Python version'
        }
        
        found_vars = {}
        for var in env_vars:
            key = var.get('key')
            if key:
                found_vars[key] = var
        
        # Check required variables
        for required_key, description in required_vars.items():
            if required_key not in found_vars:
                self.errors.append(f"❌ {description} ({required_key}) not configured")
            else:
                var_config = found_vars[required_key]
                
                if required_key == 'PROD_DATABASE_URL':
                    # Validate database URL format
                    value = var_config.get('value')
                    if value:
                        if self.validate_database_url(value):
                            self.info.append(f"✅ {required_key}: Valid PostgreSQL connection string")
                        else:
                            self.errors.append(f"❌ {required_key}: Invalid PostgreSQL connection string format")
                    else:
                        self.errors.append(f"❌ {required_key}: No value provided")
                
                elif required_key == 'PROD_SESSION_SECRET':
                    if var_config.get('generateValue'):
                        self.info.append(f"✅ {required_key}: Configured to auto-generate")
                    elif var_config.get('value'):
                        self.info.append(f"✅ {required_key}: Configured with value")
                    else:
                        self.warnings.append(f"⚠️  {required_key}: May need to be generated in Render dashboard")
                
                elif required_key == 'ENVIRONMENT':
                    value = var_config.get('value')
                    if value == 'production':
                        self.info.append(f"✅ {required_key}: Correctly set to 'production'")
                    else:
                        self.warnings.append(f"⚠️  {required_key}: Set to '{value}' (should be 'production')")
                
                elif required_key == 'PYTHON_VERSION':
                    value = var_config.get('value')
                    if value:
                        self.info.append(f"✅ {required_key}: {value}")
                    else:
                        self.errors.append(f"❌ {required_key}: No version specified")
        
        return len(self.errors) == 0
    
    def validate_database_url(self, url):
        """Validate PostgreSQL connection string format"""
        # Expected format: postgresql://user:password@host:port/dbname?params
        pattern = r'^postgresql://[^:]+:[^@]+@[^:]+:\d+/[^?]+(\?.*)?$'
        return bool(re.match(pattern, url))
    
    def validate_databases(self):
        """Validate databases configuration"""
        print("\n🗄️  Validating Databases Configuration...")
        
        if 'databases' not in self.render_config:
            self.warnings.append("⚠️  'databases' section not found (may be using external database)")
            return True
        
        databases = self.render_config['databases']
        
        if databases:
            for db in databases:
                db_name = db.get('name', 'Unknown')
                db_engine = db.get('databaseEngine', 'Unknown')
                self.info.append(f"✅ Database configured: {db_name} ({db_engine})")
        else:
            self.info.append("ℹ️  No databases managed by Render (using external database)")
        
        return True
    
    def check_local_env(self):
        """Check local environment variables"""
        print("\n🔑 Checking Local Environment Variables...")
        
        env_vars = {
            'DEV_DATABASE_URL': 'Development database URL',
            'SESSION_SECRET': 'Session secret key'
        }
        
        for var, description in env_vars.items():
            value = os.getenv(var)
            if value:
                # Mask sensitive values for display
                if 'URL' in var:
                    display = f"{value[:30]}...{value[-10:]}"
                else:
                    display = "*" * len(value)
                self.info.append(f"✅ {var}: Configured")
            else:
                self.warnings.append(f"⚠️  {var}: Not set in local .env")
    
    def check_files(self):
        """Check for critical deployment files"""
        print("\n📁 Checking Critical Files...")
        
        files_to_check = {
            'build.sh': 'Build script',
            'gunicorn.conf.py': 'Gunicorn configuration',
            'requirements.txt': 'Python dependencies',
            'migrations/alembic.ini': 'Alembic configuration',
            'main.py': 'Main application file',
        }
        
        for file_path, description in files_to_check.items():
            if Path(file_path).exists():
                self.info.append(f"✅ {description}: {file_path}")
            else:
                self.warnings.append(f"⚠️  {description}: {file_path} not found")
    
    def validate_build_script(self):
        """Validate build.sh script"""
        print("\n🔨 Validating Build Script...")
        
        if not Path('build.sh').exists():
            self.warnings.append("⚠️  build.sh not found")
            return False
        
        with open('build.sh', 'r') as f:
            content = f.read()
        
        # Check for critical commands
        critical_commands = {
            'pip install': 'Dependency installation',
            'alembic upgrade': 'Database migration',
        }
        
        for command, description in critical_commands.items():
            if command in content:
                self.info.append(f"✅ {description}: Found in build.sh")
            else:
                self.warnings.append(f"⚠️  {description}: Not found in build.sh")
        
        return True
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        # Info
        if self.info:
            print(f"\nℹ️  INFORMATION ({len(self.info)}):")
            for info in self.info:
                print(f"  {info}")
        
        # Summary
        print("\n" + "=" * 60)
        if not self.errors:
            print("✅ VALIDATION PASSED - Ready for deployment!")
            return True
        else:
            print("❌ VALIDATION FAILED - Fix errors before deployment")
            return False
    
    def run_validation(self):
        """Run complete validation"""
        print("=" * 60)
        print("🔍 RENDER CONFIGURATION VALIDATOR")
        print("=" * 60)
        print()
        
        # Load configuration
        if not self.load_render_yaml():
            self.generate_report()
            return False
        
        # Run all validations
        validations = [
            self.validate_services,
            self.validate_databases,
            self.check_local_env,
            self.check_files,
            self.validate_build_script
        ]
        
        for validation in validations:
            try:
                validation()
            except Exception as e:
                self.errors.append(f"❌ Validation error: {e}")
        
        # Generate report
        success = self.generate_report()
        
        # Recommendations
        if self.errors or self.warnings:
            print("\n💡 RECOMMENDATIONS:")
            if self.errors:
                print("  1. Fix all errors listed above")
                print("  2. Verify render.yaml configuration")
                print("  3. Check environment variables in Render dashboard")
            if self.warnings:
                print("  4. Review warnings for optimization opportunities")
        
        return success


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Render Configuration')
    parser.add_argument('--fix', action='store_true', help='Show suggested fixes')
    
    args = parser.parse_args()
    
    validator = RenderConfigValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()