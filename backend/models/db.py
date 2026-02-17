import os
import psycopg2
from psycopg2 import pool
import psycopg2.extras

# Connection pool initialized at module level
_connection_pool = None

def init_connection_pool():
    """Initialize the connection pool. Call this on app startup."""
    global _connection_pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var not set")
    
    _connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=2,
        maxconn=10,
        dsn=DATABASE_URL,
        connect_timeout=10
    )

def get_connection():
    """Get a connection from the pool with RealDictCursor."""
    global _connection_pool
    if _connection_pool is None:
        init_connection_pool()
    conn = _connection_pool.getconn()
    # Set RealDictCursor as the default cursor factory
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn

def return_connection(conn):
    """Return a connection to the pool."""
    global _connection_pool
    if _connection_pool and conn:
        _connection_pool.putconn(conn)
