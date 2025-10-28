#!/usr/bin/env python3
"""Analyze migration heads and find issues"""
import os
import re
from pathlib import Path

versions_dir = Path("migrations/versions")
py_files = sorted([f for f in versions_dir.glob("*.py") if not f.name.startswith("__")])

print('Current Migration Status:')
print('=' * 80)

# Extract revision info from all files
migrations = {}
for f in py_files:
    with open(f, 'r') as mf:
        content = mf.read()
        rev = None
        down_rev = None
        
        # Extract revision
        rev_match = re.search(r"^revision = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        if rev_match:
            rev = rev_match.group(1)
        
        # Extract down_revision
        down_rev_match = re.search(r"^down_revision = (.+?)$", content, re.MULTILINE)
        if down_rev_match:
            down_rev_str = down_rev_match.group(1).strip()
            if down_rev_str == 'None':
                down_rev = None
            else:
                down_rev = down_rev_str.strip("'\"[]")
        
        migrations[f.name] = {
            'revision': rev,
            'down_revision': down_rev,
            'path': f
        }

# Find heads (files with down_revision = None)
heads = [name for name, info in migrations.items() if info['down_revision'] is None]
print(f'\nFOUND {len(heads)} HEAD MIGRATIONS (down_revision = None):')
for head in heads:
    print(f'  - {head} (revision: {migrations[head]["revision"]})')

# Find orphaned/broken references
print(f'\nFINDING BROKEN REFERENCES:')
all_revisions = set(info['revision'] for info in migrations.values())
issues = []
for name, info in migrations.items():
    if info['down_revision'] and info['down_revision'] not in all_revisions:
        issues.append((name, info['down_revision']))
        print(f'  ⚠️  {name}')
        print(f'     Points to: {info["down_revision"]} (NOT FOUND)')

if not issues:
    print('  ✅ No broken references found')

print("\n" + "=" * 80)
print("To fix multiple heads, we need to consolidate them into a single chain.")
print("=" * 80)