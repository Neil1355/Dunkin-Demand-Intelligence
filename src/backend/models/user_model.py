from backend.models.db import get_connection
import bcrypt

def create_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
    """, (name, email, hashed))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success"}

def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        return {"status": "error", "message": "User not found"}

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"status": "error", "message": "Incorrect password"}

    return {"status": "success", "user": user}
