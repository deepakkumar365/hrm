"""
Script to fix all role checks in routes.py to use current_user.role.name
"""

import re

def fix_routes_file():
    file_path = 'E:/Gobi/Pro/HRMS/hrm/routes.py'
    
    print("\n" + "="*60)
    print("🔧 FIXING ROLE CHECKS IN ROUTES.PY")
    print("="*60)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: current_user.role in ['...', '...']
    # Replace with: (current_user.role.name if current_user.role else None) in ['...', '...']
    pattern1 = r'current_user\.role in \['
    replacement1 = r'(current_user.role.name if current_user.role else None) in ['
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: current_user.role == '...'
    # Replace with: (current_user.role.name if current_user.role else None) == '...'
    pattern2 = r'current_user\.role =='
    replacement2 = r'(current_user.role.name if current_user.role else None) =='
    content = re.sub(pattern2, replacement2, content)
    
    # Count changes
    changes = content.count('current_user.role.name') - original_content.count('current_user.role.name')
    
    if changes > 0:
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Fixed {changes} role check(s) in routes.py")
        print("\nAll instances of:")
        print("  - current_user.role in [...]")
        print("  - current_user.role == '...'")
        print("\nHave been replaced with:")
        print("  - (current_user.role.name if current_user.role else None) in [...]")
        print("  - (current_user.role.name if current_user.role else None) == '...'")
    else:
        print("\n✅ No changes needed - all role checks already use role.name")
    
    print("\n" + "="*60)
    print("✅ Done!")
    print("="*60)

if __name__ == '__main__':
    fix_routes_file()