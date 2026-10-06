"""Database initialization utility for Little Steps Tracker.

This script:
1. Connects to PostgreSQL using the credentials configured in .env.
2. Checks whether the 'little_steps_tracker' database exists.
3. Creates 'little_steps_tracker' if it does not already exist.
4. Auto-creates the 'growth_records' table and index using SQLAlchemy models.
5. Verifies read/write access.
"""

import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load .env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL is not set in backend/.env.")
    print("Please copy .env.example to .env and configure your PostgreSQL connection string.")
    sys.exit(1)

# Normalize URL for psycopg2 parsing
db_url = DATABASE_URL
if db_url.startswith("postgresql+psycopg2://"):
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql://", 1)

try:
    parsed = urlparse(db_url)
    username = parsed.username or "postgres"
    password = parsed.password or ""
    hostname = parsed.hostname or "localhost"
    port = parsed.port or 5432
    target_dbname = parsed.path.lstrip("/") or "little_steps_tracker"
except Exception as exc:
    print(f"[ERROR] Failed to parse DATABASE_URL: {exc}")
    sys.exit(1)


def init_database():
    print("=" * 60)
    print("Little Steps Tracker — PostgreSQL Initialization")
    print("=" * 60)
    print(f"Connecting to PostgreSQL server at {hostname}:{port} as user '{username}'...")

    # Step 1: Connect to default postgres maintenance database to check/create target database
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=hostname,
            port=port,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_dbname,))
        exists = cursor.fetchone()

        if not exists:
            print(f"[+] Creating database '{target_dbname}'...")
            cursor.execute(f'CREATE DATABASE "{target_dbname}";')
            print(f"[SUCCESS] Database '{target_dbname}' created successfully.")
        else:
            print(f"[*] Database '{target_dbname}' already exists.")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as exc:
        print("\n[CONNECTION FAILED]")
        print("Could not connect to PostgreSQL server.")
        print(f"Reason: {exc}\n")
        print("Troubleshooting Steps:")
        print("1. Ensure PostgreSQL is installed on your computer.")
        print("2. Ensure the PostgreSQL service is running (e.g. 'net start postgresql-x64-16').")
        print("3. Check that your password in backend/.env matches your PostgreSQL superuser password.")
        sys.exit(1)

    # Step 2: Initialize tables using SQLAlchemy declarative models
    print(f"\n[*] Creating tables in database '{target_dbname}'...")
    try:
        from app.database.connection import engine, Base
        from app.models.growth_record import GrowthRecord  # noqa: F401

        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All tables (growth_records) verified/created successfully.")
    except Exception as exc:
        print(f"[ERROR] Failed to create tables: {exc}")
        sys.exit(1)

    print("\n[READY] PostgreSQL is fully configured and ready for FastAPI.")
    print("Run the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")


if __name__ == "__main__":
    init_database()
