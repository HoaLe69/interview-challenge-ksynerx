from pathlib import Path

from sqlalchemy import create_engine, text
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text()


def init_db() -> None:
    """Idempotent 'migration': safe to run on every startup."""
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_SQL))

def check_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

