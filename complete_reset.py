#!/usr/bin/env python3
"""
Complete Database Reset Script
Drops all tables and recreates the database completely fresh.
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def complete_reset():
    """Drop all tables and recreate database completely"""
    
    # Database connection parameters
    host = os.getenv('PGHOST')
    port = os.getenv('PGPORT', '5432')
    user = os.getenv('PGUSER')
    password = os.getenv('PGPASSWORD')
    database = os.getenv('PGDATABASE')
    
    if not all([host, user, password, database]):
        print("❌ Missing database connection parameters in .env file")
        return False
    
    print(f"🔄 Connecting to database '{database}'...")
    
    try:
        # First, connect to the target database to drop all tables
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🗑️  Dropping all tables...")
        
        # Drop all tables in the public schema
        cursor.execute("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
        """)
        
        print("✅ All tables dropped successfully")
        
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
    print("🚀 Starting complete database reset...")
    
    if complete_reset():
        print("✅ Database completely reset!")
        print("\nNext steps:")
        print("1. Run: flask db upgrade")
        print("2. Run: flask seed run")
        print("3. Start your Flask application")
    else:
        print("❌ Database reset failed!")
        sys.exit(1)