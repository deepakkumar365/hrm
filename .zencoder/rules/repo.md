# Repository Info: HRM Flask App

- **Tech stack**: Flask 3, SQLAlchemy 2, Flask-SQLAlchemy, Flask-Login, PostgreSQL (psycopg2-binary)
- **Runtime**: Python 3.11
- **Entry point (dev)**: `python d:\Project\Workouts\GitHub\hrm\main.py`
- **WSGI app**: `app:app` (see `app.py`)
- **Environment**:
  - **DATABASE_URL**: PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/dbname`)
  - **SESSION_SECRET**: secret key for Flask sessions
- **DB init**: Tables auto-created at import inside `app.py` under app context

## Local development
1. Create a `.env` or set env vars in shell:
   - `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
   - `SESSION_SECRET=dev-secret`
2. Install deps:
   ```powershell
   pip install -r d:\Project\Workouts\GitHub\hrm\requirements-render.txt
   ```
3. Run dev server:
   ```powershell
   python "d:\Project\Workouts\GitHub\hrm\main.py"
   ```

## Database
- ORM models are in `models.py`.
- On app start, `db.create_all()` ensures tables exist.
- Use `dump_db.py` to export schema/data:
  ```powershell
  $env:DATABASE_URL = "postgresql://user:pass@host:5432/db"
  python "d:\Project\Workouts\GitHub\hrm\dump_db.py" --all --out "d:\Project\Workouts\GitHub\hrm\db_dump"
  ```

## Deployment
- See `render.yaml`, `Dockerfile`, and `deployment-guide.md`.
- Gunicorn config: `gunicorn.conf.py`.

## Notable modules
- `routes.py`: Flask routes
- `forms.py`: WTForms
- `singapore_payroll.py`: payroll utilities
- `utils.py`: helpers

## Notes
- Logging is enabled at DEBUG in `app.py`.
- Flask-Dance OAuth storage present but OAuth table removed.