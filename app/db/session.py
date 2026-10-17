"""SQLAlchemy session and SQLite database connection management."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings
from app.core.logging import logger

# Extract sqlite path from database_url
db_url = settings.database_url
if db_url.startswith("sqlite+aiosqlite:///"):
    sqlite_path = db_url.replace("sqlite+aiosqlite:///", "")
    sync_db_url = f"sqlite:///{sqlite_path}"
else:
    sync_db_url = db_url

if ":memory:" not in sync_db_url and "///." in sync_db_url:
    # Ensure data directory exists
    Path("./data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    sync_db_url,
    connect_args={"check_same_thread": False} if "sqlite" in sync_db_url else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in SQLite."""
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully at %s", sync_db_url)
