#!/usr/bin/env python3
"""
Helper script to update templates for the profile names refactoring.
This script shows suggested changes and can optionally make them.
"""

import re
import sys
from pathlib import Path

def find_name_patterns_in_templates():
    """Find all patterns in templates that need updating"""
    
    base_path = Path(__file__).parent / 'templates'
    
    patterns_to_find = {
        'user_first_last': {
            'regex': r'\{\{\s*current_user\.first_name\s*\}\}\s*\{\{\s*current_user\.last_name\s*\}\}',
            'replacement': '{{ current_user.full_name }}',
            'description': 'current_user first_name + last_name'
        },
        'user_first': {
            'regex': r'\{\{\s*current_user\.first_name\s*\}\}',
            'replacement': '{{ current_user.get_first_name }}',
            'description': 'current_user.first_name alone'
        },
        'user_last': {
            'regex': r'\{\{\s*current_user\.last_name\s*\}\}',
            'replacement': '{{ current_user.get_last_name }}',
            'description': 'current_user.last_name alone'
        },
        'employee_first_last': {
            'regex': r'\{\{\s*employee\.first_name\s*\}\}\s*\{\{\s*employee\.last_name\s*\}\}',
            'replacement': '{{ employee.first_name }} {{ employee.last_name }}',  # Keep as is - employee is source of truth
            'description': 'employee first_name + last_name (no change needed)'
        },
        'member_first_last': {
            'regex': r'\{\{\s*member\.first_name\s*\}\}\s*\{\{\s*member\.last_name\s*\}\}',
            'replacement': '{{ member.first_name }} {{ member.last_name }}',  # Keep as is - employee reference
            'description': 'member first_name + last_name (no change needed)'
        }
    }
    
    results = []
    
    if not base_path.exists():
        print(f"Template directory not found: {base_path}")
        return results
    
    for html_file in base_path.rglob('*.html'):
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        file_results = {
            'path': html_file.relative_to(base_path),
            'matches': [],
            'content': content
        }
        
        for i, line in enumerate(lines, 1):
            for pattern_key, pattern_info in patterns_to_find.items():
                matches = list(re.finditer(pattern_info['regex'], line))
                for match in matches:
                    file_results['matches'].append({
                        'line_num': i,
                        'pattern_key': pattern_key,
                        'pattern_description': pattern_info['description'],
                        'original': match.group(),
                        'replacement': pattern_info['replacement'],
                        'line_text': line.strip()
                    })
        
        if file_results['matches']:
            results.append(file_results)
    
    return results

def print_template_updates(results):
    """Print suggested template updates"""
    
    print("\n" + "=" * 100)
    print("TEMPLATE UPDATES - PROFILE NAMES REFACTORING")
    print("=" * 100)
    
    if not results:
        print("\n✅ No template updates needed!")
        return
    
    for file_info in results:
        print(f"\n📄 {file_info['path']}")
        print("-" * 100)
        
        for match in file_info['matches']:
            print(f"\n  Line {match['line_num']:4d}: {match['pattern_description']}")
            print(f"    FROM: {match['original']}")
            print(f"    TO:   {match['replacement']}")
            print(f"    Context: {match['line_text'][:80]}")

def apply_template_updates(results):
    """Apply template updates (with confirmation)"""
    
    if not results:
        print("\n✅ No updates needed")
        return
    
    print("\n" + "=" * 100)
    print("APPLYING TEMPLATE UPDATES")
    print("=" * 100)
    
    updated_count = 0
    skipped_count = 0
    
    for file_info in results:
        file_path = Path(__file__).parent / 'templates' / file_info['path']
        
        print(f"\n📝 Updating {file_info['path']}")
        
        # Group matches by type to avoid partial overwrites
        current_line_matches = {}
        for match in file_info['matches']:
            if match['line_num'] not in current_line_matches:
                current_line_matches[match['line_num']] = []
            current_line_matches[match['line_num']].append(match)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Apply replacements
        for line_num, matches in current_line_matches.items():
            idx = line_num - 1
            if idx < len(lines):
                updated_line = lines[idx]
                
                # Apply replacements in order (longest first to avoid conflicts)
                for match in sorted(matches, key=lambda m: len(m['original']), reverse=True):
                    if not match['replacement'].endswith('(no change needed)'):
                        updated_line = updated_line.replace(
                            match['original'],
                            match['replacement']
                        )
                        updated_count += 1
                    else:
                        skipped_count += 1
                
                lines[idx] = updated_line
                print(f"  ✓ Line {line_num} updated")
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    print(f"\n✅ Updates complete!")
    print(f"   Updated: {updated_count} patterns")
    print(f"   Skipped: {skipped_count} patterns (no change needed)")

def generate_update_instructions():
    """Generate detailed instructions for manual updates"""
    
    instructions = """
# TEMPLATE UPDATE INSTRUCTIONS

## Changes to Make

### 1. User Profile Display (current_user)
Change from:
```jinja2
{{ current_user.first_name }} {{ current_user.last_name }}
```

To:
```jinja2
{{ current_user.full_name }}
```

Or separately:
```jinja2
{{ current_user.get_first_name }} {{ current_user.get_last_name }}
```

### 2. Employee Profile Display (employee)
**NO CHANGE NEEDED** - Keep accessing directly from employee:
```jinja2
{{ employee.first_name }} {{ employee.last_name }}
```

Employee object is the source of truth for names.

### 3. Team Members (member)
**NO CHANGE NEEDED** - Keep accessing directly:
```jinja2
{{ member.first_name }} {{ member.last_name }}
```

## Priority Order for Updates

### Immediate (User-facing)
1. base.html - Navigation
2. dashboard.html - Welcome message  
3. super_admin_dashboard.html - Admin welcome
4. profile.html - Profile page
5. profile_edit.html - Profile edit form

### Soon (Employee data)
6. employees/view.html
7. employees/form.html
8. users/list.html
9. leave/list.html
10. claims/list.html

### Later (Reports)
11. payroll/*.html
12. reports/*.html
13. attendance/bulk_manage.html
14. team/team_list.html

## Testing After Update

- [ ] Load dashboard - verify welcome message shows correct name
- [ ] View profile - verify name displays correctly
- [ ] Employee list - verify all names display correctly
- [ ] Leave requests - verify employee names show correctly
- [ ] Claims - verify employee names show correctly
- [ ] Reports - verify all names display correctly

## Rollback

If you need to revert changes:
1. `git checkout templates/` (if using git)
2. Or manually revert the changes

## Notes

- The `first_name` and `last_name` columns still exist in `hrm_users` during this phase
- Using the new properties is for forward compatibility
- Employee names (employee.first_name, employee.last_name) should never change
- Only current_user accesses should be updated to use new properties
"""
    
    return instructions

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--apply':
            results = find_name_patterns_in_templates()
            print_template_updates(results)
            
            response = input("\n⚠️  Apply these updates? (yes/no): ").strip().lower()
            if response == 'yes':
                apply_template_updates(results)
            else:
                print("Update cancelled.")
        
        elif sys.argv[1] == '--instructions':
            print(generate_update_instructions())
        
        else:
            print("Unknown option. Use --apply or --instructions")
    
    else:
        # Default: show what would be updated
        results = find_name_patterns_in_templates()
        print_template_updates(results)
        
        print("\n" + "=" * 100)
        print("NEXT STEPS")
        print("=" * 100)
        print("""
1. Review the updates shown above

2. To apply updates automatically:
   python update_templates_helper.py --apply

3. For detailed instructions:
   python update_templates_helper.py --instructions

4. After updates, test thoroughly:
   - Dashboard loads
   - Profile displays correctly
   - Employee list shows correct names
   - All reports display correctly

5. Verify no regressions by running tests
""")