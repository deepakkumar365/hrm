#!/usr/bin/env python3
"""
Check what tables exist in the database
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    """Check what tables exist in the database"""
    
    # Database connection parameters
    host = os.getenv('PGHOST')
    port = os.getenv('PGPORT', '5432')
    user = os.getenv('PGUSER')
    password = os.getenv('PGPASSWORD')
    database = os.getenv('PGDATABASE')
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("📋 Existing tables in the database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check if there's any data in key tables
        key_tables = ['hrm_users', 'hrm_employee']
        for table_name in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"📊 {table_name}: {count} records")
            except psycopg2.Error:
                print(f"❌ {table_name}: Table doesn't exist")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_tables()