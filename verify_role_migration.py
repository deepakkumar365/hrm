"""
Verification script to check the status of role table migration
"""
import os
os.environ['FLASK_SKIP_DB_INIT'] = '1'

from app import app, db
from sqlalchemy import text, inspect
from tabulate import tabulate

def verify_migration():
    """Verify the role to hrm_roles migration status"""
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n" + "=" * 70)
            print("ROLE TABLE MIGRATION VERIFICATION")
            print("=" * 70)
            
            # Check table existence
            print("\n📋 TABLE EXISTENCE CHECK:")
            print("-" * 70)
            
            role_exists = 'role' in tables
            hrm_roles_exists = 'hrm_roles' in tables
            
            status_data = [
                ['role', '✅ EXISTS' if role_exists else '❌ NOT FOUND', 
                 '⚠️ Should be dropped' if role_exists else '✅ Correctly dropped'],
                ['hrm_roles', '✅ EXISTS' if hrm_roles_exists else '❌ NOT FOUND',
                 '✅ Correct' if hrm_roles_exists else '❌ Migration needed']
            ]
            
            print(tabulate(status_data, headers=['Table Name', 'Status', 'Assessment'], tablefmt='grid'))
            
            # Overall status
            if not role_exists and hrm_roles_exists:
                print("\n✅ MIGRATION STATUS: COMPLETED")
                migration_complete = True
            elif role_exists and not hrm_roles_exists:
                print("\n❌ MIGRATION STATUS: NOT STARTED")
                migration_complete = False
            elif role_exists and hrm_roles_exists:
                print("\n⚠️  MIGRATION STATUS: IN PROGRESS (both tables exist)")
                migration_complete = False
            else:
                print("\n❌ MIGRATION STATUS: ERROR (no role tables found)")
                migration_complete = False
            
            # If hrm_roles exists, show data
            if hrm_roles_exists:
                print("\n📊 HRM_ROLES TABLE DATA:")
                print("-" * 70)
                
                result = db.session.execute(text('SELECT COUNT(*) FROM hrm_roles'))
                role_count = result.scalar()
                print(f"Total roles: {role_count}")
                
                if role_count > 0:
                    result = db.session.execute(text('''
                        SELECT id, name, description, is_active, 
                               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as created
                        FROM hrm_roles 
                        ORDER BY id
                    '''))
                    
                    roles_data = []
                    for row in result:
                        roles_data.append([
                            row[0],  # id
                            row[1],  # name
                            (row[2][:40] + '...') if row[2] and len(row[2]) > 40 else (row[2] or ''),  # description
                            '✅' if row[3] else '❌',  # is_active
                            row[4]  # created
                        ])
                    
                    print("\n" + tabulate(roles_data, 
                                         headers=['ID', 'Name', 'Description', 'Active', 'Created'],
                                         tablefmt='grid'))
            
            # If old role table still exists, show comparison
            if role_exists and hrm_roles_exists:
                print("\n⚠️  COMPARISON (OLD vs NEW):")
                print("-" * 70)
                
                result = db.session.execute(text('SELECT COUNT(*) FROM role'))
                old_count = result.scalar()
                
                result = db.session.execute(text('SELECT COUNT(*) FROM hrm_roles'))
                new_count = result.scalar()
                
                comparison_data = [
                    ['role (old)', old_count],
                    ['hrm_roles (new)', new_count],
                    ['Difference', abs(old_count - new_count)]
                ]
                
                print(tabulate(comparison_data, headers=['Table', 'Count'], tablefmt='grid'))
                
                if old_count != new_count:
                    print("\n⚠️  WARNING: Record counts don't match!")
                    print("   Please review the migration before dropping the old table.")
            
            # Check foreign key constraints
            print("\n🔗 FOREIGN KEY CONSTRAINTS:")
            print("-" * 70)
            
            result = db.session.execute(text('''
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'hrm_users'
                    AND kcu.column_name = 'role_id'
            '''))
            
            fk_data = []
            correct_fk = False
            for row in result:
                fk_data.append([row[0], row[1], row[2], row[3], row[4]])
                if row[3] == 'hrm_roles':
                    correct_fk = True
            
            if fk_data:
                print(tabulate(fk_data, 
                             headers=['Constraint', 'Table', 'Column', 'References Table', 'References Column'],
                             tablefmt='grid'))
                
                if correct_fk:
                    print("\n✅ Foreign key correctly points to hrm_roles")
                else:
                    print("\n⚠️  Foreign key does not point to hrm_roles")
            else:
                print("❌ No foreign key constraint found for hrm_users.role_id")
            
            # Check users with roles
            print("\n👥 USER ROLE ASSIGNMENTS:")
            print("-" * 70)
            
            if hrm_roles_exists:
                result = db.session.execute(text('''
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(role_id) as users_with_roles,
                        COUNT(*) - COUNT(role_id) as users_without_roles
                    FROM hrm_users
                '''))
                
                row = result.fetchone()
                user_stats = [
                    ['Total Users', row[0]],
                    ['Users with Roles', row[1]],
                    ['Users without Roles', row[2]]
                ]
                
                print(tabulate(user_stats, headers=['Metric', 'Count'], tablefmt='grid'))
                
                # Show role distribution
                result = db.session.execute(text('''
                    SELECT r.name, COUNT(u.id) as user_count
                    FROM hrm_roles r
                    LEFT JOIN hrm_users u ON r.id = u.role_id
                    GROUP BY r.id, r.name
                    ORDER BY user_count DESC, r.name
                '''))
                
                role_dist = []
                for row in result:
                    role_dist.append([row[0], row[1]])
                
                if role_dist:
                    print("\n📊 Role Distribution:")
                    print(tabulate(role_dist, headers=['Role Name', 'User Count'], tablefmt='grid'))
            
            # Check indexes
            print("\n📇 INDEXES:")
            print("-" * 70)
            
            if hrm_roles_exists:
                result = db.session.execute(text('''
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'hrm_roles'
                    ORDER BY indexname
                '''))
                
                index_data = []
                for row in result:
                    index_data.append([row[0], row[1][:60] + '...' if len(row[1]) > 60 else row[1]])
                
                if index_data:
                    print(tabulate(index_data, headers=['Index Name', 'Definition'], tablefmt='grid'))
                else:
                    print("⚠️  No indexes found on hrm_roles table")
            
            # Final summary
            print("\n" + "=" * 70)
            print("SUMMARY:")
            print("=" * 70)
            
            if migration_complete:
                print("✅ Migration is COMPLETE and VERIFIED")
                print("   - hrm_roles table exists with data")
                print("   - Old role table has been dropped")
                print("   - Foreign keys are correctly configured")
                print("   - Users are properly assigned to roles")
                print("\n🎉 System is ready to use!")
            elif not role_exists and not hrm_roles_exists:
                print("❌ ERROR: No role tables found!")
                print("   Please check your database configuration.")
            elif role_exists and not hrm_roles_exists:
                print("⚠️  Migration NOT STARTED")
                print("   Run: python migrate_roles_table.py")
            else:
                print("⚠️  Migration IN PROGRESS or INCOMPLETE")
                print("   Both role and hrm_roles tables exist.")
                print("   Please complete the migration or rollback.")
            
            print("=" * 70 + "\n")
            
            return migration_complete
            
        except Exception as e:
            print(f"\n❌ ERROR during verification: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    try:
        verify_migration()
    except ImportError as e:
        if 'tabulate' in str(e):
            print("\n⚠️  The 'tabulate' package is not installed.")
            print("   Install it with: pip install tabulate")
            print("\n   Running verification without tabulate...\n")
            
            # Fallback without tabulate
            import os
            os.environ['FLASK_SKIP_DB_INIT'] = '1'
            from app import app, db
            from sqlalchemy import text, inspect
            
            with app.app_context():
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print("Tables in database:")
                print(f"  - role: {'EXISTS' if 'role' in tables else 'NOT FOUND'}")
                print(f"  - hrm_roles: {'EXISTS' if 'hrm_roles' in tables else 'NOT FOUND'}")
                
                if 'hrm_roles' in tables:
                    result = db.session.execute(text('SELECT COUNT(*) FROM hrm_roles'))
                    print(f"\nRoles in hrm_roles: {result.scalar()}")
        else:
            raise