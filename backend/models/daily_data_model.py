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

from backend.models.db import get_connection

def get_last_7_days(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.date,
            p.name AS product_name,
            d.waste
        FROM daily_data d
        JOIN products p ON d.product_id = p.id
        WHERE d.user_id = %s
          AND d.date >= CURRENT_DATE - INTERVAL '6 days'
        ORDER BY d.date;
    """, (user_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
