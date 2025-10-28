#!/usr/bin/env python3
"""Trace the complete migration chain"""
import re
from pathlib import Path

versions_dir = Path("migrations/versions")
py_files = sorted([f for f in versions_dir.glob("*.py") if not f.name.startswith("__")])

migrations = {}
rev_to_file = {}

for f in py_files:
    with open(f, 'r') as mf:
        content = mf.read()
        rev = None
        down_rev = None
        
        rev_match = re.search(r"^revision = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        if rev_match:
            rev = rev_match.group(1)
        
        down_rev_match = re.search(r"^down_revision = (.+?)$", content, re.MULTILINE)
        if down_rev_match:
            down_rev_str = down_rev_match.group(1).strip()
            if down_rev_str == 'None':
                down_rev = None
            else:
                down_rev = down_rev_str.strip("'\"[]")
        
        migrations[f.name] = {
            'revision': rev,
            'down_revision': down_rev
        }
        rev_to_file[rev] = f.name

print("=" * 80)
print("MIGRATION FILE DETAILS:")
print("=" * 80)

for filename in sorted(migrations.keys()):
    info = migrations[filename]
    rev = info['revision']
    down_rev = info['down_revision']
    next_file = rev_to_file.get(down_rev, "NOT FOUND")
    print(f"\n{filename}")
    print(f"  revision: {rev}")
    print(f"  down_revision: {down_rev}")
    if down_rev:
        print(f"  -> points to file: {next_file}")
    else:
        print(f"  -> ROOT (no parent)")

print("\n" + "=" * 80)
print("TRACING CHAIN FROM ROOT:")
print("=" * 80)

# Find root
root_rev = None
for rev, filename in rev_to_file.items():
    if migrations[filename]['down_revision'] is None:
        root_rev = rev
        break

if root_rev:
    print(f"\nStarting from root: {root_rev}")
    current_rev = root_rev
    chain = []
    depth = 0
    
    while current_rev:
        file = rev_to_file.get(current_rev)
        chain.append((current_rev, file))
        print(f"{depth+1}. {current_rev} ({file})")
        
        # Find who points to this revision
        next_rev = None
        for fname, info in migrations.items():
            if info['down_revision'] == current_rev:
                next_rev = info['revision']
                break
        
        current_rev = next_rev
        depth += 1
        if depth > 50:
            print("  [LOOP DETECTED]")
            break
    
    print(f"\nTotal migrations in chain: {len(chain)}")
else:
    print("ERROR: No root migration found!")