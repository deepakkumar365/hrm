#!/usr/bin/env python3
"""
Database Reset Script
Drops and recreates the database to fix corruption issues.
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reset_database():
    """Drop and recreate the database"""
    
    # Database connection parameters
    host = os.getenv('PGHOST')
    port = os.getenv('PGPORT', '5432')
    user = os.getenv('PGUSER')
    password = os.getenv('PGPASSWORD')
    database = os.getenv('PGDATABASE')
    
    if not all([host, user, password, database]):
        print("❌ Missing database connection parameters in .env file")
        return False
    
    print(f"🔄 Connecting to PostgreSQL server at {host}...")
    
    try:
        # Connect to PostgreSQL server (not to the specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"🗑️  Dropping database '{database}' if it exists...")
        
        # Terminate all connections to the target database
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{database}' AND pid <> pg_backend_pid();
        """)
        
        # Drop the database
        cursor.execute(f'DROP DATABASE IF EXISTS "{database}";')
        print(f"✅ Database '{database}' dropped successfully")
        
        # Create the database
        print(f"🔨 Creating database '{database}'...")
        cursor.execute(f'CREATE DATABASE "{database}";')
        print(f"✅ Database '{database}' created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database reset process...")
    
    if reset_database():
        print("✅ Database reset completed successfully!")
        print("\nNext steps:")
        print("1. Run: flask db upgrade")
        print("2. Run: flask seed run")
        print("3. Start your Flask application")
    else:
        print("❌ Database reset failed!")
        sys.exit(1)
