#!/usr/bin/env python
"""Check migration status"""
from alembic.config import Config
from alembic.script import ScriptDirectory

# Read alembic config
config = Config("migrations/alembic.ini")
script = ScriptDirectory.from_config(config)

# Get all revisions
print("=" * 60)
print("ALL MIGRATION REVISIONS:")
print("=" * 60)

for rev in script.walk_revisions():
    print(f"ID: {rev.revision}")
    print(f"  Down: {rev.down_revision}")
    print(f"  Message: {rev.message[:60]}")
    print()

# Get heads
print("\n" + "=" * 60)
print("HEAD REVISIONS (Multiple heads indicate a conflict):")
print("=" * 60)

heads = script.get_heads()
for head in heads:
    rev = script.get_revision(head)
    print(f"HEAD: {head}")
    print(f"  Message: {rev.message}")
    print()