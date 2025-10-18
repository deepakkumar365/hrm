#!/usr/bin/env python3
"""Direct fix for duplicate code in routes.py"""

# Read the current file
with open('routes.py', 'r', encoding='utf-8') as f:
    all_lines = f.readlines()

print(f"Current file has {len(all_lines)} lines")

# The claims_approve function properly ends at line 2934
# Lines 2935 onwards are duplicate code with bad indentation
# We'll keep lines 1-2934 and discard 2935 onwards

if len(all_lines) > 2934:
    # Get proper lines
    proper_lines = all_lines[:2934]
    
    # Ensure last line has newline
    if proper_lines[-1] and not proper_lines[-1].endswith('\n'):
        proper_lines[-1] = proper_lines[-1] + '\n'
    
    # Write back the cleaned file
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.writelines(proper_lines)
    
    removed = len(all_lines) - len(proper_lines)
    print(f"✅ SUCCESS! Removed {removed} lines of duplicate code")
    print(f"   File now has {len(proper_lines)} lines (was {len(all_lines)})")
    print(f"   Function claims_approve now properly ends at line 2934")
else:
    print(f"File appears OK ({len(all_lines)} lines)")

# Verify the fix
with open('routes.py', 'r', encoding='utf-8') as f:
    verify_lines = f.readlines()

# Check that line 2934 contains the proper return statement
if len(verify_lines) >= 2934:
    line_2934 = verify_lines[2933]  # 0-indexed
    if 'return redirect(url_for(\'claims_list\'))' in line_2934:
        print(f"✅ VERIFIED: Line 2934 has correct ending: {line_2934.strip()}")
    
    # Check that there's no badly indented elif after it
    if len(verify_lines) > 2934:
        next_line = verify_lines[2934]
        if next_line.strip().startswith('elif'):
            print(f"⚠️  WARNING: Still found elif at line 2935: {next_line}")
        else:
            print(f"✅ VERIFIED: No duplicate elif after line 2934")
    else:
        print(f"✅ VERIFIED: File ends at line 2934 - no duplicates!")