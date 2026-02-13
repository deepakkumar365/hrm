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
        print("--- SEARCHING FOR 'getreadytorun' IN ALL LOGS ---")
        query = """
            SELECT recipient, status, error_message, sent_at 
            FROM hrm_email_log 
            WHERE recipient ILIKE '%getreadytorun%' 
            ORDER BY sent_at DESC
        """
        logs = conn.execute(text(query)).fetchall()
        for l in logs:
             print(f"{l.sent_at} | {l.recipient:<35} | {l.status:<8} | {l.error_message}")

        if not logs:
            print("No logs found for 'getreadytorun'.")

        print("\n--- SEARCHING FOR 'getreadu' (TYPO) IN ALL LOGS ---")
        query2 = """
            SELECT recipient, status, error_message, sent_at 
            FROM hrm_email_log 
            WHERE recipient ILIKE '%getreadu%' 
            ORDER BY sent_at DESC
        """
        logs2 = conn.execute(text(query2)).fetchall()
        for l in logs2:
             print(f"{l.sent_at} | {l.recipient:<35} | {l.status:<8} | {l.error_message}")

if __name__ == "__main__":
    inspect_db()
