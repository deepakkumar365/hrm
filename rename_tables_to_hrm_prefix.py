"""
Rename existing database tables to use the `hrm_` prefix to match updated SQLAlchemy models.

Reads DATABASE_URL from env. Assumes PostgreSQL and default schema `public`.
"""
from __future__ import annotations

import os
from typing import Dict
from sqlalchemy import create_engine, text


def get_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    # Prefer psycopg3 driver when not specified
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


TABLE_RENAMES: Dict[str, str] = {
    # core app tables
    "users": "hrm_users",
    "employee": "hrm_employee",
    "payroll": "hrm_payroll",
    "attendance": "hrm_attendance",
    "leave": "hrm_leave",
    "claim": "hrm_claim",
    "appraisal": "hrm_appraisal",
    "compliance_report": "hrm_compliance_report",
    "roles": "hrm_roles",
    "departments": "hrm_departments",
    "working_hours": "hrm_working_hours",
    "work_schedules": "hrm_work_schedules",
    # legacy oauth table if present
    "flask_dance_oauth": "hrm_flask_dance_oauth",
}


def table_exists(conn, schema: str, name: str) -> bool:
    q = text(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = :schema AND table_name = :name
        """
    )
    return conn.execute(q, {"schema": schema, "name": name}).first() is not None


def main() -> int:
    engine = create_engine(get_db_url(), pool_pre_ping=True, pool_recycle=300)
    with engine.begin() as conn:
        schema = "public"
        for old, new in TABLE_RENAMES.items():
            if old == new:
                continue
            if table_exists(conn, schema, new):
                print(f"[SKIP] {schema}.{new} already exists")
                continue
            if not table_exists(conn, schema, old):
                print(f"[SKIP] {schema}.{old} does not exist")
                continue
            # Quote identifiers to be safe
            sql = text(f'ALTER TABLE "{schema}"."{old}" RENAME TO "{new}"')
            conn.execute(sql)
            print(f"[OK] Renamed {schema}.{old} -> {schema}.{new}")
    print("[DONE] Rename pass complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())