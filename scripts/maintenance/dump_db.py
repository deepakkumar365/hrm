"""
Dump all database tables' schema and data using SQLAlchemy.

Prerequisites:
- Set environment variable DATABASE_URL (e.g., postgresql://user:pass@host:5432/dbname)
- Optional: PYTHONPATH should include this repo root if running from elsewhere

Usage (Windows PowerShell):
  $env:DATABASE_URL = "your-connection-string"  # if not already set
  python "d:\Project\Workouts\GitHub\hrm\dump_db.py" --schemas public --out d:\Project\Workouts\GitHub\hrm\db_dump

Outputs:
- <out>/schema.json         : consolidated schema info
- <out>/data/<table>.csv    : one CSV per table
"""
from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    default: Any
    primary_key: bool


@dataclass
class ForeignKeyInfo:
    constrained_columns: List[str]
    referred_schema: Optional[str]
    referred_table: str
    referred_columns: List[str]


@dataclass
class TableSchema:
    schema: str
    table: str
    columns: List[ColumnInfo]
    primary_key: List[str]
    foreign_keys: List[ForeignKeyInfo]


def getenv_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. Please set it to your DB connection string."
        )
    return url


def make_engine(url: str) -> Engine:
    # Normalize URL for PostgreSQL to prefer psycopg (psycopg3)
    # Accept forms like:
    # - postgresql://... (default -> psycopg2)
    # - postgresql+psycopg://... (psycopg3)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        # Switch driver to psycopg3 if driver not specified
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # Use pool_pre_ping to avoid stale connections
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


def serialize_value(val: Any) -> Any:
    # Convert non-JSON-serializable types to strings
    if isinstance(val, (datetime, date, time)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return str(val)
    return val


def dump_table_data(engine: Engine, schema: str, table: str, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{schema}.{table}.csv"
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT * FROM "{schema}"."{table}"'))
        rows = result.fetchall()
        col_names = result.keys()

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        for row in rows:
            writer.writerow([serialize_value(v) for v in row])
    return len(rows)


def reflect_schema(engine: Engine, include_schemas: Optional[List[str]]) -> List[TableSchema]:
    insp = inspect(engine)
    schemas = include_schemas or ["public"]
    table_schemas: List[TableSchema] = []

    for sch in schemas:
        tables = insp.get_table_names(schema=sch)
        for tbl in tables:
            cols_meta = insp.get_columns(tbl, schema=sch)
            pks = insp.get_pk_constraint(tbl, schema=sch).get("constrained_columns") or []
            fks_meta = insp.get_foreign_keys(tbl, schema=sch)

            columns = [
                ColumnInfo(
                    name=c["name"],
                    type=str(c.get("type")),
                    nullable=bool(c.get("nullable")),
                    default=c.get("default"),
                    primary_key=c["name"] in pks,
                )
                for c in cols_meta
            ]
            foreign_keys = [
                ForeignKeyInfo(
                    constrained_columns=fk.get("constrained_columns", []),
                    referred_schema=fk.get("referred_schema"),
                    referred_table=fk.get("referred_table", ""),
                    referred_columns=fk.get("referred_columns", []),
                )
                for fk in fks_meta
            ]

            table_schemas.append(
                TableSchema(schema=sch, table=tbl, columns=columns, primary_key=pks, foreign_keys=foreign_keys)
            )

    return table_schemas


def save_schema_json(table_schemas: List[TableSchema], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload: List[Dict[str, Any]] = []
    for ts in table_schemas:
        payload.append(
            {
                "schema": ts.schema,
                "table": ts.table,
                "primary_key": ts.primary_key,
                "columns": [asdict(c) for c in ts.columns],
                "foreign_keys": [asdict(fk) for fk in ts.foreign_keys],
            }
        )
    (out_dir / "schema.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args(argv: List[str]):
    import argparse

    parser = argparse.ArgumentParser(description="Dump DB schema and data to files")
    parser.add_argument("--out", type=str, default=str(Path(__file__).with_name("db_dump")), help="Output directory")
    parser.add_argument(
        "--schemas",
        type=str,
        default="public",
        help="Comma-separated list of schemas to include (e.g., public,custom)",
    )
    parser.add_argument(
        "--data",
        action="store_true",
        help="Also dump table data to CSV files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Shortcut: include all non-system schemas and dump data",
    )
    return parser.parse_args(argv)


def get_all_non_system_schemas(engine: Engine) -> List[str]:
    insp = inspect(engine)
    all_schemas = insp.get_schema_names()
    return [s for s in all_schemas if s not in ("pg_catalog", "information_schema")]  # for Postgres


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    out_root = Path(args.out)

    try:
        url = getenv_database_url()
        engine = make_engine(url)
    except Exception as e:
        print(f"[ERROR] Unable to initialize engine: {e}")
        return 2

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        print(f"[ERROR] Database connection failed: {e}")
        return 3

    try:
        if args.all:
            schemas = get_all_non_system_schemas(engine)
            dump_data = True
        else:
            schemas = [s.strip() for s in args.schemas.split(",") if s.strip()]
            dump_data = args.data

        # 1) Reflect schema
        table_schemas = reflect_schema(engine, schemas)
        save_schema_json(table_schemas, out_root)
        print(f"[OK] Saved schema to: {out_root / 'schema.json'}")

        # 2) Dump data
        if dump_data:
            data_dir = out_root / "data"
            total_rows = 0
            for ts in table_schemas:
                try:
                    count = dump_table_data(engine, ts.schema, ts.table, data_dir)
                    print(f"[DATA] {ts.schema}.{ts.table}: {count} rows")
                    total_rows += count
                except SQLAlchemyError as e:
                    print(f"[WARN] Failed to dump {ts.schema}.{ts.table}: {e}")
            print(f"[OK] Data dump complete. Total rows: {total_rows}")
        else:
            print("[INFO] Data dump skipped. Use --data or --all to include table rows.")

        return 0
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
        return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
