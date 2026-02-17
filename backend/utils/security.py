"""
Rate limiting and security middleware for Flask app
Implements rate limiting on sensitive endpoints
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from flask import request, jsonify
import os

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per hour"],
    storage_uri="memory://"  # Use in-memory storage; switch to Redis for production
)

# Define rate limit strategies by endpoint type
RATE_LIMITS = {
    'auth_login': "5 per minute",  # Strict: prevent brute force
    'auth_signup': "3 per minute",  # Strict: prevent spam registrations
    'auth_forgot_password': "3 per minute",  # Strict: prevent spam
    'auth_reset_password': "5 per minute",  # Moderate
    'api_general': "100 per minute",  # Normal API calls
    'export': "10 per hour",  # Expensive operations
    'qr_download': "30 per hour",  # QR code downloads
}

def rate_limit(limit_key: str):
    """
    Decorator to apply rate limiting to a route
    
    Usage:
        @bp.route('/login', methods=['POST'])
        @rate_limit('auth_login')
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limit = RATE_LIMITS.get(limit_key, RATE_LIMITS['api_general'])
            return limiter.limit(limit)(f)(*args, **kwargs)
        return decorated_function
    return decorator


def validate_input_length(max_length: int):
    """
    Validate request body doesn't exceed max length
    Prevents large payload attacks
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() or {}
            
            # Check total body size
            content_length = request.content_length
            if content_length and content_length > (max_length * 10):
                return jsonify({"error": "Request body too large"}), 413
            
            # Check individual field sizes
            for key, value in data.items():
                if isinstance(value, str) and len(value) > max_length:
                    return jsonify({
                        "error": f"Field '{key}' exceeds maximum length of {max_length}"
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string inputs
    - Trim whitespace
    - Remove null bytes
    - Enforce max length
    """
    if not isinstance(value, str):
        return str(value)[:max_length]
    
    # Remove null bytes (SQL injection prevention)
    value = value.replace('\x00', '')
    
    # Strip and limit
    return value.strip()[:max_length]


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digits"
    
    # Special characters optional but recommended
    if not has_special:
        return True, "Password strength: Medium (special characters recommended)"
    
    return True, "Password strength: Strong"
