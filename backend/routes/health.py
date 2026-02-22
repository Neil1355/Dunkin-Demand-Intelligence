"""
Health Check Endpoint - For testing without database
Useful for development/testing when DB isn't accessible
"""
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Backend is running",
        "database_required": True
    }), 200

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
