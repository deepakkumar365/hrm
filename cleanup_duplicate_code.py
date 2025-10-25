#!/usr/bin/env python3
"""Clean up duplicate code in routes.py caused by auto-fix"""

import os

def cleanup_routes():
    """Remove the duplicate elif block from claims_approve function"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, 'routes.py')
        
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_count = len(lines)
        
        # Find lines that indicate the end of the proper claims_approve function
        # We look for: "        return redirect(url_for('claims_list'))" followed by
        # an except block, THEN followed by a badly indented elif
        
        # Strategy: Find all occurrences where we have:
        # 1. A return statement with proper indentation (8 spaces)
        # 2. Followed by except block with proper indentation
        # 3. Followed by except handler with proper indentation
        # 4. Then check if there's a badly indented elif after that
        
        has_duplicate = False
        duplicate_start = -1
        
        # Look for the pattern: properly indented except handler followed by badly indented elif
        for i in range(len(lines) - 1):
            line = lines[i]
            
            # Look for a line ending a proper except block (properly indented return)
            # that ends a claims_approve function
            if i > 0 and line.strip().startswith('return redirect(url_for('):
                # Check if the next significant line is a badly indented elif
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j]
                    # Badly indented elif - starts with exactly 3 spaces before 'elif'
                    if next_line.startswith('   elif') and not next_line.startswith('        '):
                        has_duplicate = True
                        duplicate_start = j
                        break
                
                if has_duplicate:
                    break
        
        if has_duplicate and duplicate_start > 0:
            # Remove all lines from the badly indented elif onwards
            # This includes the duplicate elif, the duplicate code, and any orphaned exception handlers
            cleaned_lines = lines[:duplicate_start]
            
            # Ensure file ends with proper newline
            if cleaned_lines and not cleaned_lines[-1].endswith('\n'):
                cleaned_lines[-1] = cleaned_lines[-1] + '\n'
            
            # Write back the cleaned file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            removed_count = original_count - len(cleaned_lines)
            print(f"[OK] Cleaned up duplicate code - removed {removed_count} lines from routes.py (from line {duplicate_start + 1})")
            return True
        
        # No duplicate found - still check if file looks complete
        # If we reach here, the file should be clean
        print(f"[OK] No duplicate code found - routes.py is clean ({original_count} lines)")
        return True
        
    except Exception as e:
        print(f"[WARNING] Could not cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False

# Execute cleanup on module import
cleanup_routes()

if __name__ == '__main__':
    cleanup_routes()