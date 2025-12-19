import os
import sys
import traceback
os.environ['ENVIRONMENT'] = 'development'
from app import app
from core.dev_utils import clean_database_hrm

with app.app_context():
    try:
        s, m = clean_database_hrm()
        print(f"Success: {s}")
        print(f"Message: {m}")
        if not s:
            sys.exit(1)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
