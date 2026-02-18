from flask import Blueprint, request, jsonify, abort
from models.user_model import create_user, authenticate_user, request_password_reset, validate_reset_token, reset_password
from utils.validation import validate_json
from utils.jwt_handler import create_access_token, create_refresh_token
import os
from services.email_service import send_password_reset_email

# Check if running in production
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER') is not None

# JSON schema for signup/login
signup_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 6},
        "store_id": {"type": "integer"},
        "phone": {"type": "string"},
        "role": {"type": "string", "enum": ["manager", "assistant_manager", "employee"]}
    },
    "required": ["name", "email", "password"],
    "additionalProperties": False,
}

login_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 6}
    },
    "required": ["email", "password"],
    "additionalProperties": False,
}

forgot_password_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"}
    },
    "required": ["email"],
    "additionalProperties": False,
}

reset_password_schema = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "password": {"type": "string", "minLength": 8}
    },
    "required": ["token", "password"],
    "additionalProperties": False,
}

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    validated = validate_json(request, signup_schema)
    if isinstance(validated, tuple):
        return validated

    name = validated.get("name")
    email = validated.get("email")
    password = validated.get("password")
    store_id = validated.get("store_id")
    phone = validated.get("phone")
    role = validated.get("role", "employee")

    result = create_user(name, email, password, store_id, phone, role)
    if result.get("status") != "success":
        return jsonify(result), 400
    
    user = result.get("user")
    # Generate JWT tokens with user and store info
    access_token = create_access_token({"sub": user["id"], "email": user["email"], "store_id": user.get("store_id", 12345)})
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Create response with httpOnly cookies
    response = jsonify({
        "status": "success",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "store_id": user.get("store_id", 12345)
        }
    })
    
    # Set secure httpOnly cookies
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=IS_PRODUCTION,  # Only require HTTPS in production
        samesite='None' if IS_PRODUCTION else 'Lax',  # None for cross-origin in prod, Lax for localhost
        max_age=30*60  # 30 minutes
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='None' if IS_PRODUCTION else 'Lax',
        max_age=7*24*60*60  # 7 days
    )
    
    return response, 201


@auth_bp.post("/login")
def login():
    validated = validate_json(request, login_schema)
    if isinstance(validated, tuple):
        return validated

    email = validated.get("email")
    password = validated.get("password")

    result = authenticate_user(email, password)
    if result.get("status") != "success":
        return jsonify(result), 401
    
    user = result.get("user")
    # Generate JWT tokens with user and store info
    access_token = create_access_token({"sub": user["id"], "email": user["email"], "store_id": user.get("store_id", 12345)})
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Create response with httpOnly cookies
    response = jsonify({
        "status": "success",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "store_id": user.get("store_id", 12345)
        }
    })
    
    # Set secure httpOnly cookies
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='None' if IS_PRODUCTION else 'Lax',
        max_age=30*60  # 30 minutes
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='None' if IS_PRODUCTION else 'Lax',
        max_age=7*24*60*60  # 7 days
    )
    
    return response, 200

@auth_bp.post("/forgot-password")
def forgot_password():
    """Request a password reset token via email.
    
    For security, always returns success even if email doesn't exist,
    but only sends email to valid users.
    """
    validated = validate_json(request, forgot_password_schema)
    if isinstance(validated, tuple):
        return validated

    email = validated.get("email")
    result = request_password_reset(email)
    
    # Send email with reset link (SendGrid configured)
    if result.get("status") == "success":
        frontend_url = os.getenv('FRONTEND_URL', 'https://dunkin-demand-intelligence.vercel.app')
        try:
            send_password_reset_email(email, result.get('token'), frontend_url)
        except Exception as e:
            # Log error but don't fail the request for security
            # (don't reveal if email sending failed)
            print(f"Email sending error: {e}")
    
    # Always return same message for security (don't reveal if email exists)
    return jsonify({"status": "success", "message": "If email exists, reset link will be sent"}), 200


@auth_bp.post("/validate-reset-token")
def validate_token():
    """Validate a password reset token without consuming it."""
    data = request.get_json() or {}
    token = data.get("token")
    
    if not token:
        return jsonify({"status": "error", "message": "Token is required"}), 400
    
    result = validate_reset_token(token)
    if result.get("status") != "success":
        return jsonify(result), 400
    
    return jsonify(result), 200


@auth_bp.post("/reset-password")
def reset_password_endpoint():
    """Reset password using a valid reset token."""
    validated = validate_json(request, reset_password_schema)
    if isinstance(validated, tuple):
        return validated

    token = validated.get("token")
    new_password = validated.get("password")

    result = reset_password(token, new_password)
    if result.get("status") != "success":
        return jsonify(result), 400
    
    return jsonify(result), 200


@auth_bp.post("/logout")
def logout():
    """Logout user by clearing authentication cookies"""
    response = jsonify({"status": "success", "message": "Logged out successfully"})
    
    # Clear the cookies
    response.delete_cookie("access_token", httponly=True, secure=IS_PRODUCTION, samesite='None' if IS_PRODUCTION else 'Lax')
    response.delete_cookie("refresh_token", httponly=True, secure=IS_PRODUCTION, samesite='None' if IS_PRODUCTION else 'Lax')
    
    return response, 200


@auth_bp.post("/refresh")
def refresh_access_token():
    """Refresh access token using refresh token"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"status": "error", "message": "Refresh token missing"}), 401
    
    from utils.jwt_handler import verify_token
    payload = verify_token(refresh_token)
    
    if "error" in payload:
        return jsonify({"status": "error", "message": "Invalid refresh token"}), 401
    
    # Generate new access token
    new_access_token = create_access_token({"sub": payload.get("sub")})
    
    response = jsonify({"status": "success", "message": "Token refreshed"})
    response.set_cookie(
        "access_token",
        new_access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='None' if IS_PRODUCTION else 'Lax',
        max_age=30*60
    )
    
    return response, 200
    return jsonify(result), 200