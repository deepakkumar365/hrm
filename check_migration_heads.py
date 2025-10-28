#!/usr/bin/env python3
"""Check Alembic heads directly"""
from alembic import command
from alembic.config import Config

# Set up Alembic config
alembic_cfg = Config('migrations/alembic.ini')

# Check current heads
print("Checking Alembic heads...")
print("=" * 80)

try:
    # Get the migration context
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import create_engine
    import os
    
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    heads = script_dir.get_heads()
    
    print(f"\nFound {len(heads)} head(s):")
    for head in heads:
        print(f"  - {head}")
    
    print("\nAll migration revisions:")
    for rev in script_dir.walk_revisions():
        print(f"  {rev.revision}: {rev.doc or '(no message)'} <- {rev.down_revision}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()