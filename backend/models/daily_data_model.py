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

def get_last_7_days(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            entry_date,
            SUM(produced) AS total_produced,
            SUM(wasted) AS total_wasted,
            SUM(produced - wasted) AS total_sold
        FROM daily_entries
        WHERE user_id = %s
        GROUP BY entry_date
        ORDER BY entry_date DESC
        LIMIT 7
    """, (user_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
