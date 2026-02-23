"""
Health Check Endpoint - For testing without database
Useful for development/testing when DB isn't accessible
"""
from flask import Blueprint, jsonify
import os
import sys

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    """Health check endpoint with database connectivity info"""
    from models.db import get_connection, _connection_pool
    
    db_status = "unknown"
    db_message = ""
    has_database_url = bool(os.getenv("DATABASE_URL"))
    
    try:
        # Try to get a connection without initializing a new pool
        if _connection_pool is not None:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            from models.db import return_connection
            return_connection(conn)
            db_status = "connected"
            db_message = "Database connection successful"
        else:
            db_status = "not_initialized"
            db_message = "Connection pool not initialized yet"
    except Exception as e:
        db_status = "failed"
        db_message = f"Database connection failed: {str(e)}"
    
    response_data = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "message": "Backend is running",
        "database": {
            "status": db_status,
            "message": db_message,
            "configured": has_database_url
        }
    }
    
    # Return 200 if backend is running, even if DB is down
    # This helps distinguish between service availability and DB issues
    return jsonify(response_data), 200

@health_bp.get("/health/db")
def health_db():
    """Explicit database connectivity check"""
    from models.db import get_connection
    
    has_database_url = bool(os.getenv("DATABASE_URL"))
    
    if not has_database_url:
        return jsonify({
            "status": "error",
            "message": "DATABASE_URL environment variable is not configured",
            "solution": "Add DATABASE_URL to your environment variables"
        }), 500
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as ping")
        result = cursor.fetchone()
        cursor.close()
        from models.db import return_connection
        return_connection(conn)
        
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "ping": result["ping"] if result else 1
        }), 200
    except Exception as e:
        error_details = str(e)
        
        # Provide helpful error messages
        if "does not resolve" in error_details or "No address associated" in error_details:
            solution = "The database hostname cannot be resolved. Check your DATABASE_URL is correct."
        elif "Network is unreachable" in error_details:
            solution = "The database server is unreachable. Check firewall/network settings."
        elif "password" in error_details.lower():
            solution = "Authentication failed. Check the password in DATABASE_URL."
        else:
            solution = f"Database error: {error_details}"
        
        response = {
            "status": "error",
            "message": f"Database connection failed",
            "error": error_details,
            "solution": solution,
            "configured": True
        }
        return jsonify(response), 500

@health_bp.get("/test-login")
def test_login():
    """
    Mock login for testing - DEVELOPMENT ONLY
    This allows testing the frontend without database connection
    """
    from utils.jwt_handler import create_access_token, create_refresh_token
    
    # Mock user data (no DB query)
    test_user = {
        "id": 999,
        "name": "Test User",
        "email": "test@example.com",
        "store_id": 12345
    }
    
    # Generate JWT tokens
    access_token = create_access_token({
        "sub": test_user["id"],
        "email": test_user["email"],
        "store_id": test_user["store_id"],
        "type": "access"
    })
    
    refresh_token = create_refresh_token({
        "sub": test_user["id"],
        "type": "refresh"
    })
    
    # Create response with httpOnly cookies
    response = jsonify({
        "status": "success",
        "user": test_user
    })
    
    # Set secure httpOnly cookies
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,  # localhost
        samesite='Lax',
        max_age=30*60  # 30 minutes
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=7*24*60*60  # 7 days
    )
    
    return response, 200

@health_bp.get("/test-logout")
def test_logout():
    """Mock logout for testing"""
    response = jsonify({"status": "success", "message": "Logged out"})
    response.set_cookie("access_token", "", max_age=0)
    response.set_cookie("refresh_token", "", max_age=0)
    return response, 200
