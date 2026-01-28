import os
import psycopg2
import psycopg2.extras

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")  # moved inside function

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var not set")

    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=10
    )