from flask import Blueprint, request, jsonify, abort
from models.user_model import create_user, authenticate_user, request_password_reset, validate_reset_token, reset_password
from utils.validation import validate_json
from utils.jwt_handler import create_access_token, create_refresh_token
import os
from services.email_service import send_password_reset_email

# JSON schema for signup/login
signup_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 6}
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

    result = create_user(name, email, password)
    return jsonify(result), 201


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
    return jsonify(result), 200

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