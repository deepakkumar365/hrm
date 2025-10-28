#!/usr/bin/env python3
"""
Diagnostic script to identify multiple head revisions and check database tables.
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor
from pathlib import Path

# Load environment variables
load_dotenv()

# Database credentials from .env
DB_HOST = os.getenv('DEV_PGHOST')
DB_PORT = os.getenv('DEV_PGPORT', '5432')
DB_NAME = os.getenv('DEV_PGDATABASE')
DB_USER = os.getenv('DEV_PGUSER')
DB_PASSWORD = os.getenv('DEV_PGPASSWORD')

print("=" * 80)
print("🔍 MIGRATION HEAD DIAGNOSIS")
print("=" * 80)

# Test database connection
print("\n📊 Database Connection:")
print(f"  Host: {DB_HOST}")
print(f"  Port: {DB_PORT}")
print(f"  Database: {DB_NAME}")
print(f"  User: {DB_USER}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor(cursor_factory=DictCursor)
    print("  ✅ Connection: SUCCESS\n")
    
    # Check alembic_version table
    print("📋 Alembic Version Table:")
    try:
        cursor.execute("SELECT version_num FROM alembic_version;")
        versions = cursor.fetchall()
        if versions:
            print(f"  Found {len(versions)} version entry(ies):")
            for v in versions:
                print(f"    - {v['version_num']}")
        else:
            print("  ⚠️  No versions recorded (empty alembic_version table)")
    except Exception as e:
        print(f"  ⚠️  alembic_version table doesn't exist: {e}")
    
    # Check existing tables
    print("\n📑 Existing Database Tables:")
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    if tables:
        print(f"  Found {len(tables)} tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
    else:
        print("  ❌ No tables found (database is empty)")
    
    conn.close()
    
except Exception as e:
    print(f"  ❌ Connection FAILED: {e}")
    sys.exit(1)

# Check migration files
print("\n🔄 Migration Files Analysis:")
versions_dir = Path("migrations/versions")
py_files = sorted([f for f in versions_dir.glob("*.py") if not f.name.startswith("__")])
sql_files = sorted([f for f in versions_dir.glob("*.sql")])

print(f"\n  Python migrations ({len(py_files)}):")
for f in py_files:
    print(f"    - {f.name}")

if sql_files:
    print(f"\n  SQL migrations ({len(sql_files)}):")
    for f in sql_files:
        print(f"    - {f.name}")

# Analyze migration headers to find multiple heads
print("\n🔗 Migration Dependency Chain:")
heads = []

for f in py_files:
    with open(f, 'r') as mf:
        content = mf.read()
        # Extract down_revision
        if "down_revision = " in content:
            for line in content.split('\n'):
                if line.startswith("down_revision"):
                    print(f"\n  {f.name}")
                    print(f"    {line.strip()}")
                    if "down_revision = None" in line:
                        heads.append(f.name)
                    break

print("\n⚠️  MULTIPLE HEAD REVISIONS FOUND:")
print(f"  Found {len(heads)} head migrations (migrations with down_revision = None):")
for head in heads:
    print(f"    - {head}")

if len(heads) > 1:
    print("\n❌ ISSUE: Multiple independent migration branches detected!")
    print("   This causes the 'Multiple head revisions' error.")
    print("\n✅ SOLUTION: Need to merge these heads or squash migrations.")
else:
    print("\n✅ Single head revision found - no branching issue.")

print("\n" + "=" * 80)