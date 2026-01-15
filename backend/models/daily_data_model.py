from backend.models.db import get_connection
import psycopg2.extras


def insert_daily_entry(user_id, product_id, entry_date, produced, waste):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO daily_entries (user_id, product_id, date, produced, waste)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, product_id, entry_date, produced, waste))

    conn.commit()
    cur.close()
    conn.close()


def get_last_7_days(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT
            p.product_name,
            de.date,
            de.produced,
            de.waste
        FROM daily_entries de
        JOIN products p ON de.product_id = p.product_id
        WHERE de.user_id = %s
        ORDER BY de.date DESC
        LIMIT 7;
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows