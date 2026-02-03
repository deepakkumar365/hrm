
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Connection details from .env
DB_URL = "postgresql://noltrion_admin:xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y@dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com/pgnoltrion"

def check_aks_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Find AKS Tenant
        print("--- Finding AKS Tenant ---")
        cur.execute("SELECT id, name, code FROM hrm_tenant WHERE name ILIKE '%AKS%'")
        tenants = cur.fetchall()
        for t in tenants:
            print(f"Tenant: {t['name']} ({t['code']}) ID: {t['id']}")

        if not tenants:
            print("No AKS tenant found.")
            return

        tenant_id = tenants[0]['id']

        # 2. Find Companies for Tenant
        print("\n--- Finding Companies ---")
        cur.execute("SELECT id, name, code FROM hrm_company WHERE tenant_id = %s", (tenant_id,))
        companies = cur.fetchall()
        company_ids = []
        for c in companies:
            print(f"Company: {c['name']} ({c['code']}) ID: {c['id']}")
            company_ids.append(c['id'])

        if not company_ids:
            print("No companies found.")
            return

        # 3. Find OT Types
        print("\n--- Finding OT Types ---")
        cur.execute("""
            SELECT id, name, code, rate_multiplier, is_fixed_rate 
            FROM hrm_ot_type 
            WHERE company_id = ANY(%s)
        """, (company_ids,))
        ot_types = cur.fetchall()
        for ot in ot_types:
            print(f"OT Type: {ot['name']} ({ot['code']}) | Rate: {ot['rate_multiplier']} | Fixed: {ot['is_fixed_rate']} | ID: {ot['id']}")

        # 4. Find Recent OT Requests (using new types)
        print("\n--- Finding Recent OT Requests ---")
        # Assuming new types have IDs from the list above
        
        cur.execute("""
            SELECT r.id, r.ot_date, r.requested_hours, r.amount, r.status, t.name as type_name, t.rate_multiplier, t.is_fixed_rate
            FROM hrm_ot_request r
            JOIN hrm_ot_type t ON r.ot_type_id = t.id
            WHERE r.company_id = ANY(%s)
            ORDER BY r.created_at DESC
            LIMIT 10
        """, (company_ids,))
        
        requests = cur.fetchall()
        for r in requests:
            print(f"Request ID: {r['id']} | Date: {r['ot_date']} | Type: {r['type_name']} | Requested (Hours/Qty): {r['requested_hours']} | Amount: {r['amount']} | Rate Multiplier: {r['rate_multiplier']} | Fixed Rate: {r['is_fixed_rate']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_aks_data()
