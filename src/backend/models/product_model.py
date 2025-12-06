from backend.models.db import get_connection

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products ORDER BY category, name")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
