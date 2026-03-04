# backend-ml/database.py
# Database connection factory.
# Uses PostgreSQL via psycopg2. Credentials come from DATABASE_URL in .env.
# Import get_conn() wherever a DB connection is needed.

import os
import psycopg2
import psycopg2.extras

# NOTE: DATABASE_URL is intentionally read inside get_conn() at call time,
# not at module import time — so load_dotenv() in main.py runs first.

def get_conn() -> psycopg2.extensions.connection:
    """
    Return a psycopg2 connection.
    RealDictCursor makes rows behave like plain dicts — same as sqlite3.Row.
    DATABASE_URL is read here (not at import time) so load_dotenv() in main.py runs first.
    """
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Copy backend-ml/.env.example → .env and fill in your Supabase connection string."
        )
    return psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
