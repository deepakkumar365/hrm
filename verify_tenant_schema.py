"""
Verify that the hrm_tenant table has all required columns
"""
import os
from app import db
from models import Tenant

if __name__ == '__main__':
    from app import app
    
    # Set environment variable to skip DB init
    os.environ['FLASK_SKIP_DB_INIT'] = '1'
    
    print("=" * 60)
    print("🔍 Verifying hrm_tenant table schema")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Try to query the tenant table with all columns
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'hrm_tenant'
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Columns in hrm_tenant table:")
            print("-" * 60)
            for row in result:
                nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                print(f"  {row[0]:<25} {row[1]:<20} {nullable}")
            
            # Try to count tenants (this was failing before)
            count = Tenant.query.count()
            print(f"\n✅ Successfully queried hrm_tenant table!")
            print(f"   Total tenants: {count}")
            
            # Try to fetch all tenants
            tenants = Tenant.query.all()
            if tenants:
                print(f"\n📊 Tenant details:")
                for tenant in tenants:
                    print(f"   - {tenant.name} ({tenant.code})")
                    print(f"     Country: {tenant.country_code or 'Not set'}")
                    print(f"     Currency: {tenant.currency_code or 'Not set'}")
            else:
                print("\n📝 No tenants found in database")
            
            print("\n" + "=" * 60)
            print("✅ Schema verification completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()