from backend.models.db import get_connection

def insert_daily_entry(user_id, product_id, date, produced, wasted):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO daily_entries (user_id, product_id, entry_date, produced, wasted)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, product_id, date, produced, wasted))

    conn.commit()
    cursor.close()
    conn.close()
