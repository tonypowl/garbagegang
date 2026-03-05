import os
from contextlib import contextmanager
import psycopg2
import psycopg2.extras

def get_conn() -> psycopg2.extensions.connection:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Copy backend-ml/.env.example → .env and fill in your Supabase connection string."
        )
    return psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)


@contextmanager
def db_conn():
    """
    Context manager for safe DB access.
    - Auto-commits on success
    - Rolls back on exception
    - Always closes the connection (no leak even if the route raises)

    Usage:
        with db_conn() as conn:
            cur = conn.cursor()
            cur.execute(...)
    """
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
