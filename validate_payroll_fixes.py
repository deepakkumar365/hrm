#!/usr/bin/env python3
"""
Comprehensive Payroll Module Validation Script
Tests all payroll fixes and verifies functionality
"""

import sys
import traceback
from datetime import datetime, date, timedelta
from decimal import Decimal

# Test utilities
class ValidationResult:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def add_pass(self, test_name):
        self.tests.append(('✅ PASS', test_name))
        self.passed += 1
    
    def add_fail(self, test_name, error):
        self.tests.append(('❌ FAIL', f"{test_name}: {error}"))
        self.failed += 1
    
    def add_warning(self, test_name, message):
        self.tests.append(('⚠️  WARN', f"{test_name}: {message}"))
        self.warnings += 1
    
    def print_report(self):
        print("\n" + "="*80)
        print("PAYROLL MODULE VALIDATION REPORT")
        print("="*80 + "\n")
        
        for status, msg in self.tests:
            print(f"{status}  {msg}")
        
        print("\n" + "="*80)
        print(f"SUMMARY: {self.passed} Passed, {self.failed} Failed, {self.warnings} Warnings")
        print("="*80 + "\n")
        
        return self.failed == 0

def validate_imports():
    """Verify all required imports work"""
    result = ValidationResult()
    
    try:
        from models import Payroll, PayrollConfiguration, Employee
        result.add_pass("Import Payroll models")
    except Exception as e:
        result.add_fail("Import Payroll models", str(e))
    
    try:
        from singapore_payroll import SingaporePayrollCalculator
        result.add_pass("Import SingaporePayrollCalculator")
    except Exception as e:
        result.add_fail("Import SingaporePayrollCalculator", str(e))
    
    try:
        from routes import payroll_list, payroll_generate, payroll_config
        result.add_pass("Import payroll routes")
    except Exception as e:
        result.add_fail("Import payroll routes", str(e))
    
    return result

def validate_models():
    """Verify Payroll models are properly defined"""
    result = ValidationResult()
    
    try:
        from models import Payroll, PayrollConfiguration
        from sqlalchemy import inspect
        
        # Check Payroll table
        payroll_mapper = inspect(Payroll)
        required_columns = [
            'id', 'employee_id', 'pay_period_start', 'pay_period_end',
            'basic_pay', 'gross_pay', 'net_pay', 'employee_cpf', 'status'
        ]
        
        existing_cols = [c.name for c in payroll_mapper.columns]
        for col in required_columns:
            if col in existing_cols:
                result.add_pass(f"Payroll column: {col}")
            else:
                result.add_fail(f"Payroll column: {col}", "Missing")
        
        # Check PayrollConfiguration table
        config_mapper = inspect(PayrollConfiguration)
        required_config_cols = [
            'id', 'employee_id', 'allowance_1_amount', 'employer_cpf',
            'employee_cpf', 'net_salary', 'remarks'
        ]
        
        existing_config_cols = [c.name for c in config_mapper.columns]
        for col in required_config_cols:
            if col in existing_config_cols:
                result.add_pass(f"PayrollConfiguration column: {col}")
            else:
                result.add_fail(f"PayrollConfiguration column: {col}", "Missing")
        
    except Exception as e:
        result.add_fail("Model structure validation", str(e))
    
    return result

def validate_calculator():
    """Verify SingaporePayrollCalculator functionality"""
    result = ValidationResult()
    
    try:
        from singapore_payroll import SingaporePayrollCalculator
        from models import Employee
        from datetime import date, timedelta
        
        calc = SingaporePayrollCalculator()
        result.add_pass("SingaporePayrollCalculator instantiation")
        
        # Test CPF rate calculation
        birth_date = date(1990, 1, 15)
        age = calc.calculate_age(birth_date)
        if 30 <= age <= 35:
            result.add_pass("Age calculation")
        else:
            result.add_warning("Age calculation", f"Age computed as {age}, expected around 33-34")
        
        # Test CPF salary ceiling
        if calc.CPF_SALARY_CEILING == 6000:
            result.add_pass("CPF salary ceiling defined")
        else:
            result.add_warning("CPF salary ceiling", f"Expected 6000, got {calc.CPF_SALARY_CEILING}")
        
        # Test AIS threshold
        if calc.AIS_THRESHOLD == 2200:
            result.add_pass("AIS threshold defined")
        else:
            result.add_warning("AIS threshold", f"Expected 2200, got {calc.AIS_THRESHOLD}")
        
        # Test CPF rates structure
        if 'citizen_pr' in calc.CPF_RATES and 'third_country' in calc.CPF_RATES:
            result.add_pass("CPF rates structure")
        else:
            result.add_fail("CPF rates structure", "Missing required rate categories")
        
    except Exception as e:
        result.add_fail("Calculator validation", str(e))
        traceback.print_exc()
    
    return result

def validate_routes():
    """Verify payroll routes have proper decorators"""
    result = ValidationResult()
    
    try:
        import inspect as py_inspect
        from routes import (payroll_list, payroll_generate, payroll_config,
                          payroll_config_update, payroll_preview_api,
                          payroll_payslip, payroll_approve)
        
        routes_to_check = [
            ('payroll_list', payroll_list),
            ('payroll_generate', payroll_generate),
            ('payroll_config', payroll_config),
            ('payroll_config_update', payroll_config_update),
            ('payroll_preview_api', payroll_preview_api),
            ('payroll_payslip', payroll_payslip),
            ('payroll_approve', payroll_approve),
        ]
        
        for route_name, route_func in routes_to_check:
            try:
                source = py_inspect.getsource(route_func)
                
                # Check if function is defined
                if route_func.__name__ == route_name:
                    result.add_pass(f"Route defined: {route_name}")
                else:
                    result.add_fail(f"Route: {route_name}", "Name mismatch")
                
                # Check for proper decorators (at least @app.route exists)
                if '@app.route' in source or '@require_login' in source:
                    result.add_pass(f"Route has decorators: {route_name}")
                else:
                    result.add_warning(f"Route decorators: {route_name}", "Check decorators manually")
                    
            except Exception as e:
                result.add_warning(f"Route analysis: {route_name}", str(e))
        
    except Exception as e:
        result.add_fail("Routes validation", str(e))
        traceback.print_exc()
    
    return result

def validate_security_checks():
    """Verify security scope checks are in place"""
    result = ValidationResult()
    
    try:
        import inspect as py_inspect
        from routes import (payroll_config_update, payroll_approve, payroll_preview_api)
        
        # Check payroll_config_update for organization check
        source = py_inspect.getsource(payroll_config_update)
        if 'organization_id' in source and 'current_user' in source:
            result.add_pass("Security: payroll_config_update checks organization")
        else:
            result.add_warning("Security: payroll_config_update", "May need organization scope check")
        
        # Check payroll_approve for organization check
        source = py_inspect.getsource(payroll_approve)
        if 'organization_id' in source:
            result.add_pass("Security: payroll_approve checks organization")
        else:
            result.add_warning("Security: payroll_approve", "May need organization scope check")
        
        # Check payroll_preview_api for organization filter
        source = py_inspect.getsource(payroll_preview_api)
        if 'organization_id' in source and 'company_id' in source:
            result.add_pass("Security: payroll_preview_api filters by organization")
        else:
            result.add_warning("Security: payroll_preview_api", "May need company scope check")
        
    except Exception as e:
        result.add_fail("Security checks validation", str(e))
    
    return result

def validate_attendance_filtering():
    """Verify attendance filtering is correct"""
    result = ValidationResult()
    
    try:
        import inspect as py_inspect
        from routes import payroll_generate, payroll_preview_api
        
        # Check payroll_generate
        source = py_inspect.getsource(payroll_generate)
        if "status='Present'" in source or 'status="Present"' in source:
            result.add_pass("Attendance filter: payroll_generate filters by Present status")
        else:
            result.add_warning("Attendance filter: payroll_generate", "May not filter by Present status")
        
        # Check payroll_preview_api
        source = py_inspect.getsource(payroll_preview_api)
        if "status='Present'" in source or 'status="Present"' in source:
            result.add_pass("Attendance filter: payroll_preview_api filters by Present status")
        else:
            result.add_warning("Attendance filter: payroll_preview_api", "May not filter by Present status")
        
    except Exception as e:
        result.add_fail("Attendance filtering validation", str(e))
    
    return result

def validate_role_decorators():
    """Verify role decorators are consistent and complete"""
    result = ValidationResult()
    
    try:
        import inspect as py_inspect
        from routes import (payroll_list, payroll_generate, payroll_config,
                          payroll_config_update, payroll_preview_api, payroll_approve)
        
        routes = [
            ('payroll_list', payroll_list, ['Super Admin', 'Tenant Admin', 'HR Manager', 'Manager']),
            ('payroll_generate', payroll_generate, ['Super Admin', 'Tenant Admin', 'HR Manager']),
            ('payroll_config', payroll_config, ['Super Admin', 'Tenant Admin', 'HR Manager']),
            ('payroll_config_update', payroll_config_update, ['Super Admin', 'Tenant Admin', 'HR Manager']),
            ('payroll_preview_api', payroll_preview_api, ['Super Admin', 'Tenant Admin', 'HR Manager']),
            ('payroll_approve', payroll_approve, ['Super Admin', 'Tenant Admin']),
        ]
        
        for route_name, route_func, expected_roles in routes:
            source = py_inspect.getsource(route_func)
            
            # Check for @require_login
            if '@require_login' in source:
                result.add_pass(f"Role decorator: {route_name} has @require_login")
            else:
                result.add_warning(f"Role decorator: {route_name}", "Missing @require_login")
            
            # Check for @require_role
            if '@require_role' in source:
                result.add_pass(f"Role decorator: {route_name} has @require_role")
                
                # Check for expected role names
                for role in expected_roles:
                    if role in source:
                        result.add_pass(f"Role in {route_name}: {role}")
                    else:
                        # Check if old role name is used
                        if role == 'Tenant Admin' and 'Admin' in source:
                            result.add_warning(f"Role in {route_name}: {role}", "May still use 'Admin' instead")
            else:
                result.add_fail(f"Role decorator: {route_name}", "Missing @require_role")
        
    except Exception as e:
        result.add_fail("Role decorator validation", str(e))
        traceback.print_exc()
    
    return result

def main():
    """Run all validation checks"""
    print("\n" + "="*80)
    print("STARTING PAYROLL MODULE VALIDATION")
    print("="*80 + "\n")
    
    all_results = []
    
    # Run all validation checks
    checks = [
        ("Imports", validate_imports),
        ("Models", validate_models),
        ("Calculator", validate_calculator),
        ("Routes", validate_routes),
        ("Security Checks", validate_security_checks),
        ("Attendance Filtering", validate_attendance_filtering),
        ("Role Decorators", validate_role_decorators),
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 Running: {check_name}...")
        try:
            result = check_func()
            all_results.append(result)
            
            # Print results
            for status, msg in result.tests:
                print(f"  {status}  {msg}")
        
        except Exception as e:
            print(f"  ❌ FAIL: {check_name} - {str(e)}")
            traceback.print_exc()
    
    # Aggregate results
    print("\n" + "="*80)
    print("FINAL VALIDATION REPORT")
    print("="*80 + "\n")
    
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_warnings = sum(r.warnings for r in all_results)
    
    print(f"Total Tests: {total_passed + total_failed + total_warnings}")
    print(f"✅ Passed:   {total_passed}")
    print(f"❌ Failed:   {total_failed}")
    print(f"⚠️  Warnings: {total_warnings}")
    
    if total_failed == 0:
        print("\n✅ ALL CRITICAL VALIDATIONS PASSED!")
        if total_warnings > 0:
            print(f"⚠️  {total_warnings} warnings found - review recommended")
        return 0
    else:
        print(f"\n❌ {total_failed} VALIDATION(S) FAILED!")
        return 1

if __name__ == '__main__':
    sys.exit(main())