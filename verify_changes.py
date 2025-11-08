import os
import sys
from jinja2 import Environment, FileSystemLoader

class MockUrlFor:
    def __call__(self, *args, **kwargs):
        return "#"

class MockUser:
    pass

class MockObject:
    def __getattr__(self, name):
        return MockObject()

try:
    env = Environment(loader=FileSystemLoader('templates'))
    env.globals['url_for'] = MockUrlFor()
    env.globals['current_user'] = MockUser()
    template = env.get_template('employees/form.html')
    
    print("[OK] Template syntax verified")
    
    test_context_add = {
        'employee': None,
        'form_data': None,
        'roles': [],
        'user_roles': [],
        'designations': [],
        'departments': [],
        'working_hours': [],
        'work_schedules': [],
        'managers': [],
        'companies': []
    }
    
    test_context_edit = test_context_add.copy()
    test_context_edit['employee'] = {'id': 1, 'first_name': 'John', 'last_name': 'Doe'}
    
    html_add = template.render(test_context_add)
    if 'Payroll Configuration' in html_add:
        print("[FAIL] ERROR: Payroll Configuration should NOT be shown in Add mode")
        sys.exit(1)
    else:
        print("[OK] Payroll Configuration correctly hidden in Add mode")
    
    html_edit = template.render(test_context_edit)
    if 'Payroll Configuration' not in html_edit:
        print("[FAIL] ERROR: Payroll Configuration should be shown in Edit mode")
        sys.exit(1)
    else:
        print("[OK] Payroll Configuration correctly shown in Edit mode")
    
    if 'basic_salary' in html_add:
        print("[FAIL] ERROR: basic_salary field should NOT be in Add mode")
        sys.exit(1)
    else:
        print("[OK] Salary fields correctly hidden in Add mode")
    
    if 'basic_salary' not in html_edit:
        print("[FAIL] ERROR: basic_salary field should be in Edit mode")
        sys.exit(1)
    else:
        print("[OK] Salary fields correctly shown in Edit mode")
    
    print("\n[PASS] All verification checks passed!")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    sys.exit(1)
