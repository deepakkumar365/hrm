#!/usr/bin/env python3
"""Truncate routes.py to remove duplicate code"""

# Read all lines
with open('routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Keep only first 2934 lines (the function ends at 2934)
# Everything from line 2935 onwards is duplicate
if len(lines) > 2934:
    truncated = lines[:2934]
    
    # Ensure proper ending with newline
    if truncated[-1] and not truncated[-1].endswith('\n'):
        truncated[-1] = truncated[-1] + '\n'
    
    # Write back
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.writelines(truncated)
    
    print(f"✅ Fixed! Removed {len(lines) - 2934} duplicate lines")
    print(f"New file: {len(truncated)} lines")
else:
    print(f"File already OK - only {len(lines)} lines")