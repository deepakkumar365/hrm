import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def check_email_logs():
    database_url = os.getenv('PROD_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_engine(database_url)
    
    # Check last few email logs
    query = """
        SELECT recipient, subject, status, error_message, sent_at 
        FROM hrm_email_log 
        ORDER BY sent_at DESC 
        LIMIT 10
    """

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            print(f"{'Recipient':<30} | {'Status':<10} | {'Sent At':<20} | {'Error'}")
            print("-" * 100)
            for row in result:
                print(f"{str(row.recipient):<30} | {str(row.status):<10} | {str(row.sent_at):<20} | {str(row.error_message)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_email_logs()
