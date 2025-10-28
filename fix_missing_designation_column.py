#!/usr/bin/env python3
"""
Emergency fix for missing designation_id column in hrm_employee table
Run this if migrations fail to apply
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

# Parse connection string
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("🔧 Checking for designation_id column...")
    
    # Check if column exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='hrm_employee' AND column_name='designation_id'
        )
    """)
    
    column_exists = cursor.fetchone()[0]
    
    if column_exists:
        print("✅ Column designation_id already exists - no action needed")
        cursor.close()
        conn.close()
        sys.exit(0)
    
    print("⏳ Adding designation_id column...")
    
    # Add column
    cursor.execute("""
        ALTER TABLE hrm_employee 
        ADD COLUMN designation_id INTEGER
    """)
    
    # Add foreign key constraint
    cursor.execute("""
        ALTER TABLE hrm_employee 
        ADD CONSTRAINT fk_hrm_employee_designation_id 
        FOREIGN KEY (designation_id) REFERENCES hrm_designation(id)
    """)
    
    conn.commit()
    print("✅ Successfully added designation_id column!")
    print("✅ Foreign key constraint created")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)