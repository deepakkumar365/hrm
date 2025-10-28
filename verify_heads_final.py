#!/usr/bin/env python3
"""Final verification of migration heads"""
import re
from pathlib import Path
from collections import defaultdict

versions_dir = Path("migrations/versions")
py_files = sorted([f for f in versions_dir.glob("*.py") if not f.name.startswith("__")])

migrations = {}
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
        
        migrations[rev] = {
            'file': f.name,
            'down_revision': down_rev
        }

# Find all heads
heads = [rev for rev, info in migrations.items() if info['down_revision'] is None]

print('=' * 80)
print(f'Found {len(heads)} head(s):')
for head in heads:
    print(f'  {head}')

# Build graph
print("\n" + "=" * 80)
print("Migration Chain:")
all_revisions = set(migrations.keys())

# Start from each head and trace the chain backwards
for head in heads:
    print(f"\nChain starting from: {head}")
    current = head
    depth = 0
    visited = set()
    while current and current not in visited:
        visited.add(current)
        info = migrations.get(current, {})
        indent = "  " * depth
        print(f"{indent}{current} <- {info['file']}")
        current = info.get('down_revision')
        depth += 1
        if depth > 50:  # Prevent infinite loops
            print(f"{indent}  [LOOP DETECTED]")
            break

# Check for orphaned references
print("\n" + "=" * 80)
print("Checking for broken references:")
for rev, info in migrations.items():
    down_rev = info['down_revision']
    if down_rev and down_rev not in all_revisions:
        print(f"  BROKEN: {rev} -> {down_rev} (NOT FOUND)")

print("\n" + "=" * 80)
if len(heads) == 1:
    print("[OK] Single head found - migration chain is valid!")
else:
    print(f"[ERROR] {len(heads)} heads found - consolidation needed!")