import os
import logging
import psycopg2
from psycopg2 import pool
import psycopg2.extras
import sys
import time

# Connection pool initialized at module level
_connection_pool = None
_logger = logging.getLogger(__name__)

def init_connection_pool(retry_count=0, max_retries=3):
    """Initialize the connection pool with retry logic. Call this on app startup."""
    global _connection_pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        error_msg = (
            "CRITICAL: DATABASE_URL environment variable is not set. "
            "Please add it to your Render environment variables. "
            "Format: postgresql://user:password@host:PORT/database?sslmode=require "
            "For Supabase on IPv4 networks: use port 6543 (connection pooler), not 5432 (direct connection)"
        )
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg)
    
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
        print("[OK] Connection pool initialized successfully", file=sys.stderr)
    except psycopg2.OperationalError as e:
        error_msg = (
            f"Database connection failed (attempt {retry_count + 1}/{max_retries + 1}): "
            f"{str(e)} | host={host} hostaddr={hostaddr} port={port}"
        )
        print(error_msg, file=sys.stderr)
        
        # Provide helpful hints for common issues
        if "does not resolve" in str(e).lower() or "name or service not known" in str(e).lower():
            print("TIP: Check that the hostname is correct in your DATABASE_URL", file=sys.stderr)
        elif "ipv" in str(e).lower() or "not compatible" in str(e).lower():
            print("TIP: IPv4/IPv6 mismatch detected! For Supabase IPv4 networks, use port 6543 (connection pooler), not 5432", file=sys.stderr)
            print("     Change: db.example.supabase.co:5432 → db.example.supabase.co:6543", file=sys.stderr)
        elif "refused" in str(e).lower():
            print("TIP: Connection refused - verify the port is correct and database is running", file=sys.stderr)
        
        if retry_count < max_retries:
            wait_time = 2 ** retry_count  # Exponential backoff: 1s, 2s, 4s
            print(f"Retrying in {wait_time}s...", file=sys.stderr)
            time.sleep(wait_time)
            return init_connection_pool(retry_count + 1, max_retries)
        else:
            raise RuntimeError(error_msg)
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
