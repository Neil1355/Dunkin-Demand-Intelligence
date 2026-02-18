"""
JWT Token Handler for Authentication
Provides token generation, validation, and refresh functionality
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict
from flask import request, jsonify, g

SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'dev-secret-key-change-in-production'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Generate JWT refresh token (longer expiration)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verify JWT token and return decoded payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        return payload
    except Exception as e:  # Catches ExpiredSignatureError and InvalidTokenError
        error_name = type(e).__name__
        if error_name == "ExpiredSignatureError":
            return {"error": "Token expired"}
        else:
            return {"error": "Invalid token"}


def require_auth(f):
    """Decorator to require valid JWT token for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Debug logging
        print(f"[AUTH DEBUG] Cookies received: {list(request.cookies.keys())}")
        print(f"[AUTH DEBUG] Authorization header: {request.headers.get('Authorization', 'None')}")
        
        # Check for token in Authorization header (Bearer scheme)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
                print(f"[AUTH DEBUG] Token from header: {token[:20]}...")
            except IndexError:
                return jsonify({"status": "error", "message": "Invalid authorization header"}), 401
        
        # Fallback: check for token in secure cookie (httpOnly)
        if not token and 'access_token' in request.cookies:
            token = request.cookies.get('access_token')
            print(f"[AUTH DEBUG] Token from cookie: {token[:20] if token else 'None'}...")
        
        if not token:
            print("[AUTH DEBUG] No token found!")
            return jsonify({"status": "error", "message": "Authorization token missing"}), 401
        
        # Verify token
        payload = verify_token(token)
        if "error" in payload:
            print(f"[AUTH DEBUG] Token verification failed: {payload['error']}")
            return jsonify({"status": "error", "message": payload["error"]}), 401
        
        print(f"[AUTH DEBUG] Token verified successfully for user_id: {payload.get('sub')}")
        
        # Store user info in Flask's g object (request context)
        g.user_id = payload.get("sub")
        g.store_id = payload.get("store_id")
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_store_access(store_id_param='store_id'):
    """Decorator to verify user has access to specific store"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First run auth decorator
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({"status": "error", "message": "Invalid authorization header"}), 401
            
            if not token and 'access_token' in request.cookies:
                token = request.cookies.get('access_token')
            
            if not token:
                return jsonify({"status": "error", "message": "Authorization token missing"}), 401
            
            payload = verify_token(token)
            if "error" in payload:
                return jsonify({"status": "error", "message": payload["error"]}), 401
            
            # Store user info in Flask's g object (request context)
            g.user_id = payload.get("sub")
            g.store_id = payload.get("store_id")
            
            # Now verify store access
            requested_store_id = kwargs.get(store_id_param) or request.args.get(store_id_param)
            if requested_store_id and int(requested_store_id) != g.store_id:
                return jsonify({"status": "error", "message": "Unauthorized access to this store"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
