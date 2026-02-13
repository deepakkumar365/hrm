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
        # 1. Get recipients for all schedules
        print("--- SCHEDULES ---")
        rows = conn.execute(text("SELECT id, tenant_id, recipients FROM hrm_report_schedule")).fetchall()
        for r in rows:
             print(f"Schedule {r.id} (Tenant {r.tenant_id}): {r.recipients}")

        # 2. Get latest logs for these recipients
        print("\n--- RECENT LOGS ---")
        logs = conn.execute(text("SELECT recipient, status, error_message, sent_at, tenant_id FROM hrm_email_log ORDER BY sent_at DESC LIMIT 30")).fetchall()
        for l in logs:
             print(f"{l.sent_at} | {l.recipient:<35} | {l.status:<8} | T:{l.tenant_id} | {l.error_message}")

        # 3. Check Configs
        print("\n--- CONFIGS ---")
        configs = conn.execute(text("SELECT tenant_id, provider, is_active FROM hrm_email_config")).fetchall()
        for c in configs:
            print(f"Tenant {c.tenant_id} | Provider: {c.provider} | Active: {c.is_active}")

if __name__ == "__main__":
    inspect_db()
