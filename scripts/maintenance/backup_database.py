#!/usr/bin/env python3
"""
Database Backup Utility
Safe backup of both development and production databases
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

class DatabaseBackup:
    def __init__(self):
        self.dev_url = os.getenv('DEV_DATABASE_URL')
        self.prod_url = os.getenv('PROD_DATABASE_URL')
        self.backup_dir = Path(__file__).parent / 'db_backups'
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def parse_db_url(self, url):
        """Parse PostgreSQL connection URL"""
        try:
            # URL format: postgresql://user:password@host:port/database
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/'),
            }
        except Exception as e:
            print(f"❌ Error parsing database URL: {e}")
            return None
    
    def backup_database_pg_dump(self, db_name, url, output_file):
        """Backup database using pg_dump"""
        try:
            db_config = self.parse_db_url(url)
            if not db_config:
                return False
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config['password']:
                env['PGPASSWORD'] = db_config['password']
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-F', 'c',  # Custom format (compressed)
                '-f', output_file
            ]
            
            print(f"  Backing up {db_name}...")
            print(f"  Host: {db_config['host']}")
            print(f"  Database: {db_config['database']}")
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                file_size = Path(output_file).stat().st_size / (1024*1024)
                print(f"  ✅ Backup successful: {file_size:.2f} MB")
                return True
            else:
                print(f"  ❌ Backup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ Backup timed out (>5 minutes)")
            return False
        except Exception as e:
            print(f"  ❌ Backup error: {e}")
            return False
    
    def backup_database_sqlalchemy(self, db_name, url, output_file):
        """Backup database using SQLAlchemy (slower but more portable)"""
        try:
            print(f"  Backing up {db_name} (SQLAlchemy method)...")
            
            engine = create_engine(url)
            
            # Get table names
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            with open(output_file, 'w') as f:
                f.write(f"-- Database Backup: {db_name}\n")
                f.write(f"-- Timestamp: {datetime.now()}\n")
                f.write(f"-- Tables: {len(tables)}\n\n")
                f.write("BEGIN;\n\n")
                
                with engine.connect() as conn:
                    for table in tables:
                        print(f"    Exporting {table}...", end=" ", flush=True)
                        
                        # Get table schema
                        result = conn.execute(text(f"SELECT * FROM {table}"))
                        rows = result.fetchall()
                        
                        if rows:
                            columns = result.keys()
                            col_str = ', '.join(f'"{col}"' for col in columns)
                            
                            # Write INSERT statements
                            for row in rows:
                                values = ', '.join([
                                    f"'{str(val).replace(chr(39), chr(39)*2)}'" if val is not None else 'NULL'
                                    for val in row
                                ])
                                f.write(f'INSERT INTO "{table}" ({col_str}) VALUES ({values});\n')
                            
                            print(f"✅ ({len(rows)} records)")
                        else:
                            print("(empty)")
                
                f.write("\nCOMMIT;\n")
            
            file_size = Path(output_file).stat().st_size / (1024*1024)
            print(f"  ✅ Backup successful: {file_size:.2f} MB")
            return True
            
        except Exception as e:
            print(f"  ❌ Backup error: {e}")
            return False
    
    def verify_backup(self, backup_file):
        """Verify backup file exists and is valid"""
        try:
            if not Path(backup_file).exists():
                print(f"  ❌ Backup file not found: {backup_file}")
                return False
            
            size = Path(backup_file).stat().st_size
            if size == 0:
                print(f"  ❌ Backup file is empty")
                return False
            
            size_mb = size / (1024*1024)
            print(f"  ✅ Backup verified: {size_mb:.2f} MB")
            return True
            
        except Exception as e:
            print(f"  ❌ Verification error: {e}")
            return False
    
    def backup_development(self):
        """Backup development database"""
        print("\n📦 BACKING UP DEVELOPMENT DATABASE")
        print("-" * 60)
        
        backup_file = self.backup_dir / f'dev_backup_{self.timestamp}.sql'
        
        # Try pg_dump first
        if self.backup_database_pg_dump('Development', self.dev_url, str(backup_file)):
            if self.verify_backup(backup_file):
                return str(backup_file)
        
        # Fallback to SQLAlchemy
        print("  Retrying with SQLAlchemy method...")
        if self.backup_database_sqlalchemy('Development', self.dev_url, str(backup_file)):
            if self.verify_backup(backup_file):
                return str(backup_file)
        
        return None
    
    def backup_production(self):
        """Backup production database"""
        print("\n📦 BACKING UP PRODUCTION DATABASE")
        print("-" * 60)
        
        backup_file = self.backup_dir / f'prod_backup_{self.timestamp}.sql'
        
        # Try pg_dump first
        if self.backup_database_pg_dump('Production', self.prod_url, str(backup_file)):
            if self.verify_backup(backup_file):
                return str(backup_file)
        
        # Fallback to SQLAlchemy
        print("  Retrying with SQLAlchemy method...")
        if self.backup_database_sqlalchemy('Production', self.prod_url, str(backup_file)):
            if self.verify_backup(backup_file):
                return str(backup_file)
        
        return None
    
    def list_backups(self):
        """List all available backups"""
        print("\n📋 AVAILABLE BACKUPS")
        print("-" * 60)
        
        backups = sorted(self.backup_dir.glob('*.sql'))
        
        if not backups:
            print("No backups found")
            return
        
        for backup in backups[-10:]:  # Show last 10
            size_mb = backup.stat().st_size / (1024*1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  • {backup.name} ({size_mb:.2f} MB) - {mtime}")
        
        if len(backups) > 10:
            print(f"  ... and {len(backups) - 10} older backups")
    
    def cleanup_old_backups(self, keep_count=10):
        """Delete old backups, keeping only the most recent"""
        print(f"\n🧹 CLEANING UP OLD BACKUPS (keeping {keep_count} most recent)")
        print("-" * 60)
        
        backups = sorted(self.backup_dir.glob('*.sql'), key=lambda x: x.stat().st_mtime)
        
        if len(backups) <= keep_count:
            print(f"  ℹ️  Only {len(backups)} backups found, nothing to clean")
            return
        
        to_delete = backups[:-keep_count]
        
        for backup in to_delete:
            try:
                size_mb = backup.stat().st_size / (1024*1024)
                backup.unlink()
                print(f"  🗑️  Deleted: {backup.name} ({size_mb:.2f} MB)")
            except Exception as e:
                print(f"  ❌ Error deleting {backup.name}: {e}")
    
    def run_backup(self, mode='full', cleanup=True):
        """Execute backup based on mode"""
        print("=" * 60)
        print("🔒 DATABASE BACKUP UTILITY")
        print("=" * 60)
        
        dev_backup = None
        prod_backup = None
        
        if mode in ['full', 'dev']:
            dev_backup = self.backup_development()
        
        if mode in ['full', 'prod']:
            prod_backup = self.backup_production()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 BACKUP SUMMARY")
        print("=" * 60)
        
        if dev_backup:
            print(f"✅ Development backup: {Path(dev_backup).name}")
        if prod_backup:
            print(f"✅ Production backup: {Path(prod_backup).name}")
        
        print(f"\n📁 Backups location: {self.backup_dir}")
        
        # List recent backups
        self.list_backups()
        
        # Cleanup
        if cleanup and mode == 'full':
            self.cleanup_old_backups()
        
        print("\n" + "=" * 60)
        print("✅ BACKUP COMPLETE")
        print("=" * 60 + "\n")
        
        return dev_backup, prod_backup


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Utility')
    parser.add_argument('--mode', choices=['full', 'dev', 'prod'], default='full',
                       help='Backup mode: full, dev only, or prod only')
    parser.add_argument('--list', action='store_true', help='List existing backups')
    parser.add_argument('--cleanup', type=int, help='Keep N most recent backups (default: 10)')
    
    args = parser.parse_args()
    
    backup = DatabaseBackup()
    
    if args.list:
        backup.list_backups()
    elif args.cleanup:
        backup.cleanup_old_backups(args.cleanup)
    else:
        backup.run_backup(mode=args.mode, cleanup=args.cleanup is None)


if __name__ == '__main__':
    main()
