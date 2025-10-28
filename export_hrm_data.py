#!/usr/bin/env python3
"""
Export HRM data from PostgreSQL database to INSERT statements
This creates a backup of all HRM table data as SQL INSERT statements
"""

import os
import psycopg2
from datetime import datetime

# Database connection details from .env
DB_HOST = os.getenv('DEV_PGHOST', 'dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com')
DB_PORT = int(os.getenv('DEV_PGPORT', 5432))
DB_NAME = os.getenv('DEV_PGDATABASE', 'pgnoltrion')
DB_USER = os.getenv('DEV_PGUSER', 'noltrion_admin')
DB_PASSWORD = os.getenv('DEV_PGPASSWORD', 'xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y')

# Only HRM-related tables
HRM_TABLES = [
    'role',
    'hrm_tenant',
    'hrm_company',
    'organization',
    'hrm_users',
    'hrm_employee',
    'hrm_designation',
    'hrm_working_hours',
    'hrm_work_schedules',
    'hrm_employee_bank_info',
    'hrm_employee_documents',
    'hrm_payroll',
    'hrm_payroll_configuration',
    'hrm_attendance',
    'hrm_leave',
    'hrm_claim',
    'hrm_appraisal',
    'hrm_roles',
    'hrm_departments',
    'hrm_compliance_report',
    'hrm_tenant_payment_config',
    'hrm_role_access_control',
    'hrm_user_role_mapping',
    'hrm_tenant_documents'
]

def escape_value(value):
    """Escape SQL values properly"""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    else:
        return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"

def get_columns(cursor, table_name):
    """Get column names and types for a table"""
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    return cursor.fetchall()

def export_table_data(cursor, table_name):
    """Export data from a single table as INSERT statements"""
    try:
        # Get columns
        columns_info = get_columns(cursor, table_name)
        if not columns_info:
            return f"-- Table '{table_name}' not found or has no columns\n\n", 0
        
        columns = [col[0] for col in columns_info]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            return f"-- Table '{table_name}' is empty\n\n", 0
        
        # Get data
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY 1 LIMIT 1000")
        rows = cursor.fetchall()
        
        # Build SQL
        sql_lines = [f"\n-- ============================================"]
        sql_lines.append(f"-- TABLE: {table_name.upper()} ({len(rows)} rows)")
        sql_lines.append(f"-- ============================================")
        sql_lines.append(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES")
        
        value_lines = []
        for row in rows:
            values = []
            for i, col in enumerate(columns):
                values.append(escape_value(row[i]))
            value_lines.append(f"  ({', '.join(values)})")
        
        sql_lines.append(',\n'.join(value_lines) + ';')
        sql_lines.append(f"\n")
        
        return '\n'.join(sql_lines), len(rows)
    
    except Exception as e:
        return f"-- Error exporting {table_name}: {str(e)}\n\n", 0

def main():
    print("🔄 Connecting to database...\n")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        conn.set_isolation_level(0)  # autocommit mode
        cursor = conn.cursor()
        print("✅ Connected successfully!\n")
        
        print(f"📊 Exporting {len(HRM_TABLES)} HRM tables\n")
        
        # Export data
        print("📝 Exporting data...\n")
        all_sql = []
        total_rows = 0
        
        all_sql.append("-- ============================================")
        all_sql.append("-- HRM DATABASE EXPORT - ALL TABLES DATA")
        all_sql.append(f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        all_sql.append("-- ============================================")
        all_sql.append("")
        
        for i, table_name in enumerate(HRM_TABLES, 1):
            print(f"[{i:2d}/{len(HRM_TABLES)}] {table_name:40s}", end=" ", flush=True)
            
            sql, row_count = export_table_data(cursor, table_name)
            all_sql.append(sql)
            total_rows += row_count
            
            if row_count == 0:
                print("(empty)")
            else:
                print(f"✅ {row_count:4d} rows")
        
        # Write to file
        output_file = "c:\\Repo\\hrm\\EXPORTED_DATA.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_sql))
        
        print(f"\n{'='*60}")
        print(f"✅ EXPORT COMPLETE!")
        print(f"{'='*60}")
        print(f"📁 File: {output_file}")
        print(f"📊 Total Rows: {total_rows}")
        print(f"📋 Total Tables: {len(HRM_TABLES)}")
        print(f"\nNext Steps:")
        print(f"1. Open the file in a text editor to review the data")
        print(f"2. Import this file in pgAdmin using: File > Create Script")
        print(f"3. Or run: psql -U user -d database -f {output_file}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check database credentials in .env file")
        print("2. Ensure PostgreSQL database is running and accessible")
        print("3. Verify network connectivity to the database server")
        return False
    
    return True

if __name__ == "__main__":
    main()