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
        print("--- RECIPIENTS IN DB ---")
        rows = conn.execute(text("SELECT id, recipients FROM hrm_report_schedule")).fetchall()
        for r in rows:
             print(f"Schedule {r.id}: {repr(r.recipients)}")

        print("\n--- RECENT LOGS (PAIRS) ---")
        logs = conn.execute(text("SELECT recipient, status, error_message, sent_at FROM hrm_email_log ORDER BY sent_at DESC LIMIT 10")).fetchall()
        for l in logs:
             print(f"Time: {l.sent_at} | Recipient: {repr(l.recipient)} | Status: {l.status} | Err: {l.error_message}")

if __name__ == "__main__":
    inspect_db()
