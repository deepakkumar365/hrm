#!/usr/bin/env python3
"""
Helper script to track and validate the profile names refactoring.
This script helps identify all places using user.first_name/last_name
and validates the transition.
"""

import os
import re
from pathlib import Path

def find_name_references():
    """Find all references to first_name and last_name in the codebase"""
    
    base_path = Path(__file__).parent
    
    # Patterns to find
    patterns = {
        'user_first_name': r'user\.first_name|current_user\.first_name',
        'user_last_name': r'user\.last_name|current_user\.last_name',
        'employee_first_name': r'employee\.first_name',
        'employee_last_name': r'employee\.last_name',
        'in_templates': r'\.first_name|\.last_name',  # General pattern in templates
    }
    
    results = {
        'python_files': [],
        'template_files': [],
        'summary': {}
    }
    
    print("=" * 80)
    print("SCANNING CODEBASE FOR PROFILE NAME REFERENCES")
    print("=" * 80)
    
    # Scan Python files
    print("\n🔍 Scanning Python files...")
    for py_file in base_path.rglob('*.py'):
        if '.git' in py_file.parts or '__pycache__' in py_file.parts:
            continue
        if 'refactor_profile_names' in py_file.name:
            continue
            
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        file_results = {
            'path': str(py_file.relative_to(base_path)),
            'matches': []
        }
        
        for i, line in enumerate(lines, 1):
            for pattern_name, pattern in patterns.items():
                if pattern_name.startswith('in_templates'):
                    continue
                matches = re.finditer(pattern, line)
                for match in matches:
                    file_results['matches'].append({
                        'line': i,
                        'pattern': pattern_name,
                        'text': line.strip(),
                        'column': match.start()
                    })
        
        if file_results['matches']:
            results['python_files'].append(file_results)
    
    # Scan template files
    print("🔍 Scanning template files...")
    for html_file in base_path.rglob('*.html'):
        if '.git' in html_file.parts or '__pycache__' in html_file.parts:
            continue
        
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        file_results = {
            'path': str(html_file.relative_to(base_path)),
            'matches': []
        }
        
        for i, line in enumerate(lines, 1):
            # Look for patterns like {{ something.first_name }}
            matches = re.finditer(r'\{\{[^}]*\.first_name[^}]*\}\}|\{\{[^}]*\.last_name[^}]*\}\}', line)
            for match in matches:
                file_results['matches'].append({
                    'line': i,
                    'text': line.strip(),
                    'column': match.start()
                })
        
        if file_results['matches']:
            results['template_files'].append(file_results)
    
    return results

def print_results(results):
    """Print the scan results in a nice format"""
    
    print("\n" + "=" * 80)
    print("SCAN RESULTS")
    print("=" * 80)
    
    # Python files
    print(f"\n📄 Python Files ({len(results['python_files'])} files with references):")
    print("-" * 80)
    
    for file_info in results['python_files']:
        print(f"\n   {file_info['path']}")
        for match in file_info['matches'][:5]:  # Show first 5
            print(f"      Line {match['line']:4d}: {match['pattern']:20s} → {match['text'][:70]}")
        if len(file_info['matches']) > 5:
            print(f"      ... and {len(file_info['matches']) - 5} more matches")
    
    # Template files
    print(f"\n🎨 Template Files ({len(results['template_files'])} files with references):")
    print("-" * 80)
    
    for file_info in results['template_files']:
        print(f"\n   {file_info['path']}")
        for match in file_info['matches'][:5]:  # Show first 5
            print(f"      Line {match['line']:4d}: {match['text'][:70]}")
        if len(file_info['matches']) > 5:
            print(f"      ... and {len(file_info['matches']) - 5} more matches")

def generate_migration_checklist():
    """Generate a checklist for the migration"""
    
    checklist = """
# PROFILE NAMES REFACTORING CHECKLIST

## Phase 1: Data Preparation ✓
- [x] Add properties to User model (get_first_name, get_last_name, full_name)
- [x] Create migration script (migrate_profile_names.py)
- [ ] Run migration script: `python migrate_profile_names.py`
- [ ] Verify all users have employee profiles

## Phase 2: Code Updates
### Models
- [x] Add properties to User model

### Routes (E:/Gobi/Pro/HRMS/hrm/routes.py)
- [ ] Line 186-187: Update user registration to use employee profile
- [ ] Line 728-729: Update employee creation flow
- [ ] Line 1834, 1836, 1967: Update audit logs to use get_first_name/get_last_name

### Other Python Files
- [ ] update auth.py if needed
- [ ] update replit_auth.py if needed
- [ ] update cli_commands.py if needed

### Templates
Critical templates to update:
- [ ] templates/base.html (line 310)
- [ ] templates/dashboard.html (line 11)
- [ ] templates/super_admin_dashboard.html (line 11)
- [ ] templates/profile.html (lines 16, 42)
- [ ] templates/profile_edit.html (line 30)
- [ ] templates/employees/form.html (line 53)
- [ ] templates/employees/view.html (lines 3, 20, 53, 170)
- [ ] templates/users/list.html (line 34)
- [ ] templates/payroll/*.html
- [ ] templates/leave/list.html
- [ ] templates/claims/list.html
- [ ] templates/attendance/bulk_manage.html

### API Serialization
- [ ] Update any API endpoints that serialize user names

## Phase 3: Testing
- [ ] Test login with various users
- [ ] Verify profile pages display correct names
- [ ] Check audit logs show correct names
- [ ] Verify reports show correct employee names
- [ ] Test employee creation flow

## Phase 4: Cleanup (After verification)
- [ ] Create migration to drop first_name from hrm_users
- [ ] Create migration to drop last_name from hrm_users
- [ ] Remove name columns from User model
- [ ] Remove name properties from User model
- [ ] Remove migration scripts

## Notes
- During transition, both hrm_users and hrm_employee have name columns
- User.get_first_name and User.get_last_name provide access to employee names with fallback
- Templates should gradually transition to using .get_first_name and .get_last_name
- Eventually, all name access will come through the employee_profile relationship
"""
    
    return checklist

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--checklist':
        print(generate_migration_checklist())
    else:
        results = find_name_references()
        print_results(results)
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
1. Run the migration script:
   python migrate_profile_names.py

2. Review the scan results above to see where names are used

3. Update the code systematically:
   - Start with critical paths (login, profile display)
   - Use User.get_first_name and User.get_last_name properties
   - Update templates gradually

4. For a detailed checklist:
   python refactor_profile_names_helper.py --checklist

5. After completing all updates and testing, drop the redundant columns
""")
