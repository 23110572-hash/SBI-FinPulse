"""Database connection + session management. PostgreSQL (Neon) only."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. FinPulse uses PostgreSQL (Neon) only — "
        "set DATABASE_URL in backend/.env (e.g. postgresql+psycopg2://USER:PASS@HOST/DB?sslmode=require)."
    )
if settings.database_url.startswith("sqlite"):
    raise RuntimeError(
        "SQLite is no longer supported. Set DATABASE_URL to your Neon PostgreSQL connection string."
    )

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (no-op for tables that already exist)."""
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    """Drop and recreate ALL tables. Destructive — used by seeding."""
    from . import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
