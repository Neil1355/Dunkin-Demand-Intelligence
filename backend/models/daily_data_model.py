from db import get_connection
from psycopg2.extras import RealDictCursor


def insert_daily_entry(user_id, product_id, date, produced, waste):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO public.daily_entries (user_id, product_id, date, produced, waste)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, product_id, date)
        DO UPDATE SET
            produced = EXCLUDED.produced,
            waste = EXCLUDED.waste
        """,
        (user_id, product_id, date, produced, waste),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_last_7_days(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            p.name AS product_name,
            AVG(d.waste) AS avg_waste
        FROM daily_data d
        JOIN products p ON d.product_id = p.id
        WHERE d.user_id = %s
          AND d.date >= CURDATE() - INTERVAL 7 DAY
        GROUP BY p.name
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows
