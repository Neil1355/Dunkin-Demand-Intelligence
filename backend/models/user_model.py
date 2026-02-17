from models.db import get_connection, return_connection
import bcrypt
from psycopg2.extras import RealDictCursor
import secrets
from datetime import datetime, timedelta


def create_user(name, email, password, store_id=None, phone=None, role="employee"):
    """Create a new user and store a bcrypt password hash.

    Returns a safe user dict (id, name, email, created_at, store_id, phone, role) on success.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # hash and store as utf-8 string
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

        # Use default store_id if not provided
        if store_id is None:
            store_id = 12345

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, store_id, phone, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, email, created_at, store_id, phone, role
            """,
            (name, email, hashed, store_id, phone, role),
        )

        user = cursor.fetchone()
        conn.commit()
        return {"status": "success", "user": user}
    finally:
        return_connection(conn)


def authenticate_user(email, password):
    """Authenticate user by email and password.

    Returns a safe user dict (id, name, email, created_at) on success.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            "SELECT id, name, email, created_at, store_id, password_hash FROM users WHERE email=%s",
            (email,),
        )
        user = cursor.fetchone()

        if not user:
            return {"status": "error", "message": "User not found"}

        pw_hash = user.get("password_hash")
        if not pw_hash:
            return {"status": "error", "message": "No password set for user"}

        if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
            return {"status": "error", "message": "Incorrect password"}

        # remove password_hash from returned user
        safe_user = {
            "id": user["id"],
            "name": user["name"],
            "email": user.get("email"),
            "created_at": user.get("created_at"),
            "store_id": user.get("store_id", 12345),
        }

        return {"status": "success", "user": safe_user}
    finally:
        return_connection(conn)


def request_password_reset(email):
    """Generate a password reset token and store it in the database.
    
    Returns token and expiration info on success.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            # For security, don't reveal if email exists
            return {"status": "success", "message": "If email exists, reset link will be sent"}

        # Generate secure token
        token = secrets.token_urlsafe(32)
        user_id = user["id"]
        expires_at = datetime.utcnow() + timedelta(hours=1)

        #Store token
        cursor.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, token, expires_at),
        )

        conn.commit()
        return {"status": "success", "token": token, "email": email, "expires_at": expires_at.isoformat()}
    finally:
        return_connection(conn)


def validate_reset_token(token):
    """Validate a password reset token.
    
    Returns user info if token is valid and not expired.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT prt.id, prt.user_id, prt.expires_at, u.email, u.name
            FROM password_reset_tokens prt
            JOIN users u ON prt.user_id = u.id
            WHERE prt.token = %s AND prt.used_at IS NULL
            """,
            (token,),
        )
        token_record = cursor.fetchone()

        if not token_record:
            return {"status": "error", "message": "Invalid or expired token"}

        # Check expiration
        if datetime.fromisoformat(token_record["expires_at"].isoformat()) < datetime.utcnow():
            return {"status": "error", "message": "Token has expired"}

        return {
            "status": "success",
            "user_id": token_record["user_id"],
            "email": token_record["email"],
            "name": token_record["name"],
        }
    finally:
        return_connection(conn)


def reset_password(token, new_password):
    """Reset user password using a valid reset token.
    
    Returns success/error status.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Validate token
        cursor.execute(
            """
            SELECT prt.id, prt.user_id, prt.expires_at
            FROM password_reset_tokens prt
            WHERE prt.token = %s AND prt.used_at IS NULL
            """,
            (token,),
        )
        token_record = cursor.fetchone()

        if not token_record:
            return {"status": "error", "message": "Invalid or already-used token"}

        # Check expiration
        expires_at = token_record.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        if expires_at < datetime.utcnow():
            return {"status": "error", "message": "Token has expired"}

        # Hash new password
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
        user_id = token_record["user_id"]
        token_id = token_record["id"]

        # Update password and mark token as used
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE id=%s",
            (hashed, user_id),
        )

        cursor.execute(
            "UPDATE password_reset_tokens SET used_at=NOW() WHERE id=%s",
            (token_id,),
        )

        conn.commit()
        return {"status": "success", "message": "Password reset successfully"}
    finally:
        return_connection(conn)
