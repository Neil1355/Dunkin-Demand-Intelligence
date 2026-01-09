from .db import get_connection

def insert_daily_entry(user_id, product_id, entry_date, produced, wasted):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO daily_entries (user_id, product_id, entry_date, produced, wasted)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, product_id, entry_date, produced, wasted))

    conn.commit()
    cursor.close()
    conn.close()

def get_last_7_days(user_id=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if user_id is None:
        cur.execute("""
            SELECT date, product_id, produced, wasted
            FROM daily_data
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
    else:
        cur.execute("""
            SELECT date, product_id, produced, wasted
            FROM daily_data
            WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """, (user_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
