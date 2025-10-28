#!/usr/bin/env python3
"""
Production Health Check
Monitors production application and database health
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

class ProductionHealthChecker:
    def __init__(self, app_url='https://noltrion-hrm.render.com'):
        self.app_url = app_url
        self.prod_url = os.getenv('PROD_DATABASE_URL')
        self.db_engine = None
        self.checks = {}
        
    def check_application(self):
        """Check if application is running"""
        print("🌐 Checking Application Health...")
        
        try:
            # Try health endpoint
            response = requests.get(f'{self.app_url}/health', timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        print("  ✅ Application: RUNNING")
                        self.checks['application'] = 'healthy'
                        return True
                except:
                    pass
            
            # Try home page
            response = requests.get(f'{self.app_url}/', timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print("  ✅ Application: RUNNING")
                self.checks['application'] = 'healthy'
                return True
            else:
                print(f"  ⚠️  Application: HTTP {response.status_code}")
                self.checks['application'] = f'http_{response.status_code}'
                return False
                
        except requests.exceptions.Timeout:
            print("  ❌ Application: TIMEOUT (check Render dashboard)")
            self.checks['application'] = 'timeout'
            return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Application: UNREACHABLE (check Render service status)")
            self.checks['application'] = 'unreachable'
            return False
        except Exception as e:
            print(f"  ❌ Application: ERROR ({e})")
            self.checks['application'] = str(e)
            return False
    
    def check_database(self):
        """Check if database is accessible"""
        print("\n💾 Checking Database Health...")
        
        try:
            self.db_engine = create_engine(self.prod_url, echo=False, pool_pre_ping=True)
            
            with self.db_engine.connect() as conn:
                # Simple connectivity test
                result = conn.execute(text("SELECT 1;"))
                result.scalar()
                
                print("  ✅ Database: CONNECTED")
                self.checks['database_connection'] = 'connected'
                
                # Check table count
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """))
                table_count = result.scalar()
                print(f"  ✅ Tables: {table_count} found")
                self.checks['table_count'] = table_count
                
                return True
                
        except Exception as e:
            print(f"  ❌ Database: ERROR ({e})")
            self.checks['database_connection'] = str(e)
            return False
    
    def check_master_data(self):
        """Check if master data exists"""
        print("\n📊 Checking Master Data...")
        
        if not self.db_engine:
            print("  ⚠️  Database not connected, skipping master data check")
            return False
        
        try:
            with self.db_engine.connect() as conn:
                tables = {
                    'organization': 'Organizations',
                    'role': 'Roles',
                    'designation': 'Designations',
                    'leave_type': 'Leave Types'
                }
                
                all_ok = True
                for table, name in tables.items():
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = result.scalar()
                    
                    if count > 0:
                        print(f"  ✅ {name}: {count} records")
                        self.checks[f'master_data_{table}'] = count
                    else:
                        print(f"  ⚠️  {name}: 0 records")
                        all_ok = False
                        self.checks[f'master_data_{table}'] = 0
                
                return all_ok
                
        except Exception as e:
            print(f"  ❌ Master data check failed: {e}")
            return False
    
    def check_users(self):
        """Check if users exist"""
        print("\n👥 Checking User Accounts...")
        
        if not self.db_engine:
            return False
        
        try:
            with self.db_engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM hrm_users;"))
                user_count = result.scalar()
                
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM hrm_users WHERE is_active = true;
                """))
                active_count = result.scalar()
                
                print(f"  ℹ️  Total users: {user_count}")
                print(f"  ℹ️  Active users: {active_count}")
                
                self.checks['total_users'] = user_count
                self.checks['active_users'] = active_count
                
                if user_count == 0:
                    print("  ⚠️  No users found (may need admin setup)")
                    return False
                
                return True
                
        except Exception as e:
            print(f"  ❌ User check failed: {e}")
            return False
    
    def check_performance(self):
        """Check response time"""
        print("\n⚡ Checking Performance...")
        
        try:
            import time
            
            start = time.time()
            response = requests.get(f'{self.app_url}/health', timeout=10)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            if elapsed < 500:
                status = "GOOD"
                emoji = "✅"
            elif elapsed < 2000:
                status = "ACCEPTABLE"
                emoji = "⚠️"
            else:
                status = "SLOW"
                emoji = "🐢"
            
            print(f"  {emoji} Response time: {elapsed:.0f}ms ({status})")
            self.checks['response_time_ms'] = elapsed
            
            return elapsed < 2000
            
        except Exception as e:
            print(f"  ⚠️  Could not measure performance: {e}")
            return False
    
    def generate_report(self):
        """Generate health check report"""
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK REPORT")
        print("=" * 60)
        print(f"Timestamp: {datetime.now()}")
        print(f"Application URL: {self.app_url}")
        
        print("\n🔍 Summary:")
        print(f"  Checks performed: {len(self.checks)}")
        
        # Count failures
        failures = sum(1 for k, v in self.checks.items() 
                      if v in ['timeout', 'unreachable', 'connection_error', 0])
        
        if failures == 0:
            print("  ✅ All checks passed")
            return True
        else:
            print(f"  ⚠️  {failures} check(s) with issues")
            return False
    
    def run_all_checks(self):
        """Run all health checks"""
        print("=" * 60)
        print("🏥 PRODUCTION HEALTH CHECK")
        print("=" * 60)
        print(f"Started: {datetime.now()}\n")
        
        checks = [
            self.check_application,
            self.check_database,
            self.check_master_data,
            self.check_users,
            self.check_performance
        ]
        
        results = []
        for check in checks:
            try:
                result = check()
                results.append(result)
            except Exception as e:
                print(f"❌ Check failed: {e}")
                results.append(False)
        
        success = self.generate_report()
        
        return success
    
    def continuous_monitor(self, interval=300):
        """Continuously monitor health (every 5 minutes)"""
        import time
        
        print("🔄 Starting continuous monitoring...")
        print(f"Check interval: {interval} seconds\n")
        
        check_count = 0
        while True:
            check_count += 1
            print(f"\n{'='*60}")
            print(f"Check #{check_count} - {datetime.now()}")
            print(f"{'='*60}")
            
            self.checks = {}
            try:
                self.check_application()
                self.check_database()
                self.check_performance()
            except KeyboardInterrupt:
                print("\n\n👋 Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
            
            print(f"\n⏱️  Next check in {interval} seconds...")
            time.sleep(interval)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Health Check')
    parser.add_argument('--url', default='https://noltrion-hrm.render.com',
                       help='Application URL')
    parser.add_argument('--monitor', action='store_true',
                       help='Continuous monitoring mode')
    parser.add_argument('--interval', type=int, default=300,
                       help='Monitoring interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    checker = ProductionHealthChecker(app_url=args.url)
    
    if args.monitor:
        try:
            checker.continuous_monitor(interval=args.interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
            sys.exit(0)
    else:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()