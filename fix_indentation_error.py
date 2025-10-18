#!/usr/bin/env python3
"""Fix the indentation error in routes.py"""

import sys

def fix_indentation_error():
    """Remove the duplicate elif block from claims_approve function"""
    try:
        # Read the file
        with open('D:/Projects/HRMS/hrm/routes.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and remove the duplicate code (lines with bad indentation)
        # We need to remove lines starting at line 2934 (0-indexed: 2934)
        # The duplicate starts with "   elif action" (incorrectly indented)
        
        new_lines = []
        skip_until = -1
        
        for i, line in enumerate(lines):
            # Skip the duplicate section (badly indented elif and everything after)
            if i == 2934:  # Line 2935 (1-indexed) is index 2934 (0-indexed)
                # Mark that we should skip to the end of file
                skip_until = len(lines)
            
            if i < skip_until:
                new_lines.append(line)
        
        # Write back the fixed file
        with open('D:/Projects/HRMS/hrm/routes.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("✅ Fixed indentation error - removed duplicate code from claims_approve function")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing indentation: {e}")
        return False

if __name__ == '__main__':
    if fix_indentation_error():
        sys.exit(0)
    else:
        sys.exit(1)