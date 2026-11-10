from pathlib import Path
import hashlib
import time
from contextvars import ContextVar
import streamlit as st
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from core.config import database_url

MIGRATION_LOCK = 728422012

_query_stats = ContextVar("query_stats", default=None)


def reset_query_stats():
    _query_stats.set({"duration_ms": 0.0, "count": 0, "slowest_ms": 0.0})


def query_stats():
    return dict(_query_stats.get() or {"duration_ms": 0.0, "count": 0, "slowest_ms": 0.0})


def _track_query(started):
    elapsed=(time.perf_counter()-started)*1000
    current=query_stats()
    current["duration_ms"] += elapsed
    current["count"] += 1
    current["slowest_ms"] = max(current["slowest_ms"], elapsed)
    _query_stats.set(current)

@st.cache_resource
def pool():
    p = ConnectionPool(
        conninfo=database_url(),
        min_size=1,
        max_size=5,
        kwargs={"row_factory": dict_row, "autocommit": False},
        open=True,
    )
    p.wait(timeout=20)
    return p


def execute(sql, params=(), returning=False):
    with pool().connection() as c:
        with c.cursor() as cur:
            started=time.perf_counter()
            try:
                cur.execute(sql, params)
            finally:
                _track_query(started)
            row = cur.fetchone() if returning else None
        c.commit()
        return row


def fetch_all(sql, params=()):
    with pool().connection() as c:
        with c.cursor() as cur:
            started=time.perf_counter()
            try:
                cur.execute(sql, params)
            finally:
                _track_query(started)
            return cur.fetchall()


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def _checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _ensure_migration_registry(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations(
                version VARCHAR(120) PRIMARY KEY,
                checksum VARCHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    conn.commit()


def _apply_file_once(conn, path, version):
    checksum = _checksum(path)
    with conn.cursor() as cur:
        cur.execute("SELECT checksum FROM schema_migrations WHERE version=%s", (version,))
        existing = cur.fetchone()
        if existing:
            if existing["checksum"] != checksum:
                raise RuntimeError(f"La migración {version} cambió después de haber sido aplicada.")
            return False
        cur.execute(Path(path).read_text(encoding="utf-8"))
        cur.execute(
            "INSERT INTO schema_migrations(version,checksum) VALUES(%s,%s)",
            (version, checksum),
        )
    conn.commit()
    return True


def init_database():
    """Serialize schema initialization and execute every migration at most once."""
    root = Path(__file__).parents[1]
    with pool().connection() as conn:
        # Session-level advisory lock protects Streamlit reruns / concurrent sessions.
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_LOCK,))
        try:
            _ensure_migration_registry(conn)
            _apply_file_once(conn, root / "database/schema.sql", "000_baseline")
            for path in sorted((root / "database/migrations").glob("*.sql")):
                _apply_file_once(conn, path, path.name)
        except Exception:
            # PostgreSQL rejects any further SQL on an aborted transaction.
            # Restore the connection before trying to release the advisory lock.
            conn.rollback()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_unlock(%s)", (MIGRATION_LOCK,))
                conn.commit()
            except Exception:
                conn.rollback()
            raise
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s)", (MIGRATION_LOCK,))
            conn.commit()
