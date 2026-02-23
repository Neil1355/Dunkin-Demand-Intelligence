import os
import logging
import psycopg2
from psycopg2 import pool
import psycopg2.extras
import sys

# Connection pool initialized at module level
_connection_pool = None
_logger = logging.getLogger(__name__)

def init_connection_pool():
    """Initialize the connection pool. Call this on app startup."""
    global _connection_pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var not set")
    
    try:
        # Parse the DATABASE_URL to extract components and force IPv4.
        # This avoids IPv6-only attempts that can fail on some hosts.
        import socket
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)

        host = parsed.hostname
        port = parsed.port or 5432
        hostaddr = None
        if host:
            try:
                # Prefer the first IPv4 address if available.
                infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                if infos:
                    hostaddr = infos[0][4][0]
                    _logger.info("Resolved %s to IPv4: %s", host, hostaddr)
            except Exception as exc:
                _logger.error("DNS resolution failed for %s: %s", host, exc)
                hostaddr = None

        connection_params = {
            'host': host,
            'hostaddr': hostaddr,
            'port': port,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'connect_timeout': 10,
            'sslmode': 'require',
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
        error_msg = (
            "Failed to initialize connection pool: "
            f"{str(e)} | host={host} hostaddr={hostaddr} port={port} sslmode=require"
        )
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
