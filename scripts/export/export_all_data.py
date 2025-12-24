#!/usr/bin/env python3
"""
Export all data from PostgreSQL database to INSERT statements
This creates a complete backup of all table data as SQL INSERT statements
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connection details from .env
DB_URL = os.getenv('DEV_DATABASE_URL', 'postgresql://noltrion_admin:xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y@dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com/pgnoltrion')
DB_HOST = os.getenv('DEV_PGHOST', 'dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com')
DB_PORT = int(os.getenv('DEV_PGPORT', 5432))
DB_NAME = os.getenv('DEV_PGDATABASE', 'pgnoltrion')
DB_USER = os.getenv('DEV_PGUSER', 'noltrion_admin')
DB_PASSWORD = os.getenv('DEV_PGPASSWORD', 'xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y')

def get_all_tables(cursor):
    """Get all table names from the database"""
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    return [row[0] for row in cursor.fetchall()]

def get_columns(cursor, table_name):
    """Get column names and types for a table"""
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    return cursor.fetchall()

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
        return f"'{str(value)}'"

def get_row_count(cursor, table_name):
    """Get row count for a table"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def export_table_data(cursor, table_name):
    """Export data from a single table as INSERT statements"""
    
    # Get row count
    count = get_row_count(cursor, table_name)
    if count == 0:
        return f"-- Table '{table_name}' is empty\n\n"
    
    # Get columns
    columns_info = get_columns(cursor, table_name)
    columns = [col[0] for col in columns_info]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1")
    rows = cursor.fetchall()
    
    # Build SQL
    sql_lines = [f"\n-- ============================================"]
    sql_lines.append(f"-- TABLE: {table_name.upper()} ({count} rows)")
    sql_lines.append(f"-- ============================================")
    sql_lines.append(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES")
    
    value_lines = []
    for row in rows:
        values = [escape_value(row[col]) for col in columns]
        value_lines.append(f"  ({', '.join(values)})")
    
    sql_lines.append(',\n'.join(value_lines) + ';')
    sql_lines.append(f"\n")
    
    return '\n'.join(sql_lines)

def main():
    print("🔄 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        print("✅ Connected successfully!\n")
        
        # Get all tables
        tables = get_all_tables(cursor)
        print(f"📊 Found {len(tables)} tables")
        print(f"Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}\n")
        
        # Export data
        print("📝 Exporting data...\n")
        all_sql = []
        
        all_sql.append("-- ============================================")
        all_sql.append("-- DATABASE EXPORT - ALL TABLES DATA")
        all_sql.append(f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        all_sql.append("-- ============================================")
        all_sql.append("")
        
        for i, table_name in enumerate(tables, 1):
            print(f"[{i}/{len(tables)}] Exporting {table_name}...", end=" ")
            try:
                sql = export_table_data(cursor, table_name)
                all_sql.append(sql)
                # Count rows in this table
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"✅ ({count} rows)")
            except Exception as e:
                print(f"⚠️  Error: {str(e)}")
                all_sql.append(f"-- Error exporting {table_name}: {str(e)}\n\n")
        
        # Write to file
        output_file = "EXPORTED_DATA_ALL.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_sql))
        
        print(f"\n✅ Export complete!")
        print(f"📁 Saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("EXPORT SUMMARY")
        print("="*50)
        
        for table_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  {table_name}: {count} rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check database credentials in .env")
        print("2. Ensure database is accessible")
        print("3. Verify PostgreSQL is running")
        return False
    
    return True

if __name__ == "__main__":
    main()