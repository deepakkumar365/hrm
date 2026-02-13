import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def inspect_db():
    database_url = os.getenv('PROD_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not database_url: return

    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        print("--- LOG DATA (Today) ---")
        # Logs from 2026-02-13
        query = """
            SELECT recipient, status, error_message, sent_at, tenant_id 
            FROM hrm_email_log 
            WHERE sent_at >= '2026-02-13 00:00:00'
            ORDER BY sent_at ASC
        """
        logs = conn.execute(text(query)).fetchall()
        for l in logs:
             print(f"{l.sent_at} | {l.recipient:<35} | {l.status:<8} | T:{l.tenant_id} | {l.error_message}")

        print("\n--- ALL SCHEDULES ---")
        rows = conn.execute(text("SELECT id, tenant_id, recipients, is_active FROM hrm_report_schedule")).fetchall()
        for r in rows:
             print(f"ID: {r.id} | Active: {r.is_active} | Tenant: {r.tenant_id} | Recipients: {r.recipients}")

if __name__ == "__main__":
    inspect_db()
