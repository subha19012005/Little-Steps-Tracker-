"""Database connection and session configuration for Little Steps Tracker.

This module initializes the SQLAlchemy engine, session maker, and declarative
base using the DATABASE_URL environment variable.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file if present
load_dotenv()

# Default PostgreSQL connection string for local development
# Format: postgresql://<username>:<password>@<host>:<port>/<dbname>
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/little_steps_tracker"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# SQLAlchemy 2 defaults postgresql:// to psycopg (psycopg 3).
# If postgresql:// is provided with psycopg2-binary installed, normalize to postgresql+psycopg2://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# SQLAlchemy engine
# pool_pre_ping ensures stale connections are re-verified before use
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

# Thread-local database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base model for SQLAlchemy
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a SQLAlchemy database session per request.

    Ensures the session is cleanly closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
