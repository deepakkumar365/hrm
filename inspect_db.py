import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def inspect_db():
    database_url = os.getenv('PROD_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_engine(database_url)
    
    # 1. Check Schedules
    print("--- Report Schedules ---")
    query_sched = "SELECT id, report_type, recipients, tenant_id FROM hrm_report_schedule"
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_sched))
            for row in result:
                print(f"ID: {row.id} | Type: {row.report_type} | Tenant: {row.tenant_id} | Recipients: {row.recipients}")
    except Exception as e:
        print(f"Error Sched: {e}")

    # 2. Check Email Logs more thoroughly
    print("\n--- Recent Email Logs ---")
    query_logs = "SELECT recipient, status, error_message, sent_at, tenant_id FROM hrm_email_log ORDER BY sent_at DESC LIMIT 20"
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_logs))
            for row in result:
                print(f"{str(row.sent_at)} | {str(row.recipient):<35} | {row.status:<8} | T:{row.tenant_id} | {row.error_message}")
    except Exception as e:
        print(f"Error Logs: {e}")

    # 3. Check Email Config for the tenant
    print("\n--- Email Configs ---")
    query_config = "SELECT tenant_id, provider, is_active, smtp_host FROM hrm_email_config"
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_config))
            for row in result:
                print(f"Tenant: {row.tenant_id} | Provider: {row.provider} | Active: {row.is_active} | Host: {row.smtp_host}")
    except Exception as e:
        print(f"Error Config: {e}")

if __name__ == "__main__":
    inspect_db()
