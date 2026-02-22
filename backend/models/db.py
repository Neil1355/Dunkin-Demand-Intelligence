import os
import psycopg2
from psycopg2 import pool
import psycopg2.extras
import sys

# Connection pool initialized at module level
_connection_pool = None

def init_connection_pool():
    """Initialize the connection pool. Call this on app startup."""
    global _connection_pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var not set")
    
    try:
        # Parse the DATABASE_URL to extract components and force IPv4
        # This prevents IPv6 connection attempts which fail on Render's free tier
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        # Build connection params with gai_resolve_addresses to prefer IPv4
        connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'connect_timeout': 10,
            'sslmode': 'require',
            # Force resolution to IPv4 addresses only
            'target_session_attrs': 'any',
        }
        
        # Filter out None values
        connection_params = {k: v for k, v in connection_params.items() if v is not None}
        
        _connection_pool = pool.SimpleConnectionPool(
            minconn=2,
            maxconn=10,
            **connection_params
        )
        print("✓ Connection pool initialized successfully", file=sys.stderr)
    except Exception as e:
        error_msg = f"Failed to initialize connection pool: {str(e)}"
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg)

def get_connection():
    """Get a connection from the pool with RealDictCursor."""
    global _connection_pool
    if _connection_pool is None:
        init_connection_pool()
    if _connection_pool is None:
        raise RuntimeError("Connection pool initialization failed")
    conn = _connection_pool.getconn()
    # Set RealDictCursor as the default cursor factory
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn

def return_connection(conn):
    """Return a connection to the pool."""
    global _connection_pool
    if _connection_pool and conn:
        _connection_pool.putconn(conn)
