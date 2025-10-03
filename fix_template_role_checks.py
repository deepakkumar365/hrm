"""
Script to fix all role checks in template files to use current_user.role.name
"""

import os
import re
from pathlib import Path

def fix_template_files():
    templates_dir = Path('E:/Gobi/Pro/HRMS/hrm/templates')
    
    print("\n" + "="*70)
    print("🔧 FIXING ROLE CHECKS IN TEMPLATE FILES")
    print("="*70)
    
    # Find all HTML files
    html_files = list(templates_dir.rglob('*.html'))
    
    total_changes = 0
    files_modified = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_changes = 0
        
        # Pattern 1: {{ current_user.role }} (display only, not in comparisons)
        # Replace with: {{ current_user.role.name if current_user.role else 'None' }}
        pattern1 = r'\{\{\s*current_user\.role\s*\}\}'
        replacement1 = r'{{ current_user.role.name if current_user.role else \'None\' }}'
        new_content = re.sub(pattern1, replacement1, content)
        if new_content != content:
            file_changes += new_content.count('current_user.role.name') - content.count('current_user.role.name')
            content = new_content
        
        # Pattern 2: current_user.role in ['...', '...']
        # Replace with: (current_user.role.name if current_user.role else None) in ['...', '...']
        pattern2 = r'current_user\.role in \['
        replacement2 = r'(current_user.role.name if current_user.role else None) in ['
        new_content = re.sub(pattern2, replacement2, content)
        if new_content != content:
            file_changes += new_content.count('current_user.role.name') - content.count('current_user.role.name')
            content = new_content
        
        # Pattern 3: current_user.role == '...'
        # Replace with: (current_user.role.name if current_user.role else None) == '...'
        pattern3 = r'current_user\.role =='
        replacement3 = r'(current_user.role.name if current_user.role else None) =='
        new_content = re.sub(pattern3, replacement3, content)
        if new_content != content:
            file_changes += new_content.count('current_user.role.name') - content.count('current_user.role.name')
            content = new_content
        
        # Pattern 4: current_user.role != '...'
        # Replace with: (current_user.role.name if current_user.role else None) != '...'
        pattern4 = r'current_user\.role !='
        replacement4 = r'(current_user.role.name if current_user.role else None) !='
        new_content = re.sub(pattern4, replacement4, content)
        if new_content != content:
            file_changes += new_content.count('current_user.role.name') - content.count('current_user.role.name')
            content = new_content
        
        if content != original_content:
            # Write back
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_modified += 1
            total_changes += file_changes
            relative_path = html_file.relative_to(templates_dir)
            print(f"\n✅ Fixed {file_changes} instance(s) in: {relative_path}")
    
    print("\n" + "="*70)
    print(f"📊 SUMMARY")
    print("="*70)
    print(f"   Files modified: {files_modified}")
    print(f"   Total changes: {total_changes}")
    print("\n✅ All template files have been updated!")
    print("="*70)

if __name__ == '__main__':
    fix_template_files()