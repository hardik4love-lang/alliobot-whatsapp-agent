import sqlite3
import uuid
from typing import Optional, Any, List, Dict
from loguru import logger
from app.config import settings
from app.database import SQLITE_DB_PATH, init_sqlite_db

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

class DBAdapter:
    """
    Dual-engine Database Adapter:
    Tries PostgreSQL first; if not running, transparently uses SQLite (alliobot.db).
    Ensures seamless execution on Windows with zero Docker/Postgres installation.
    """
    def __init__(self):
        self.is_postgres = False
        self._test_connection()

    def _test_connection(self):
        if HAS_PSYCOPG2:
            try:
                conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=1)
                conn.close()
                self.is_postgres = True
                logger.info("Connected to PostgreSQL database.")
                return
            except Exception:
                pass
        self.is_postgres = False
        init_sqlite_db()
        logger.info(f"Using native Windows SQLite database: {SQLITE_DB_PATH}")

    def get_connection(self):
        if self.is_postgres:
            return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH, timeout=20.0)
            conn.row_factory = sqlite3.Row
            return conn

    def format_query(self, query: str) -> str:
        if self.is_postgres:
            return query
        # Translate Postgres syntax to SQLite syntax
        q = query.replace("%s", "?")
        q = q.replace("NOW()", "CURRENT_TIMESTAMP")
        q = q.replace("gen_random_uuid()", f"'{str(uuid.uuid4())}'")
        return q

db = DBAdapter()
