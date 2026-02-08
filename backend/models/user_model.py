from models.db import get_connection
import bcrypt
from psycopg2.extras import RealDictCursor


def create_user(name, email, password):
    """Create a new user and store a bcrypt password hash.

    Returns a safe user dict (id, name, email, created_at) on success.
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # hash and store as utf-8 string
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    cursor.execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id, name, email, created_at
        """,
        (name, email, hashed),
    )

    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "user": user}


def authenticate_user(email, password):
    """Authenticate user by email and password.

    Returns a safe user dict (id, name, email, created_at) on success.
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT id, name, email, created_at, password_hash FROM users WHERE email=%s",
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
    }

    cursor.close()
    conn.close()

    return {"status": "success", "user": safe_user}
