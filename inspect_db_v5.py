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
        print("--- LOG DATA (Around 10:24 AM) ---")
        query = """
            SELECT recipient, status, error_message, sent_at, tenant_id 
            FROM hrm_email_log 
            WHERE sent_at >= '2026-02-13 10:20:00' AND sent_at <= '2026-02-13 10:30:00'
            ORDER BY sent_at ASC
        """
        logs = conn.execute(text(query)).fetchall()
        if not logs:
            print("No logs found in this range.")
        for l in logs:
             print(f"{l.sent_at} | {l.recipient:<35} | {l.status:<8} | {l.error_message}")

        print("\n--- SCHEDULE 2 RECIPIENTS ---")
        rows = conn.execute(text("SELECT recipients FROM hrm_report_schedule WHERE id = 2")).fetchall()
        for r in rows:
             print(f"Recipients: {repr(r.recipients)}")

if __name__ == "__main__":
    inspect_db()
