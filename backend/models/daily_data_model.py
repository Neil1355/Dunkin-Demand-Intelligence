from backend.models.db import get_connection
from psycopg2.extras import RealDictCursor


def insert_daily_entry(user_id, product_id, date, produced, waste):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO daily_entries (user_id, product_id, date, produced, waste)
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

    cur.execute(
        """
        SELECT
            p.product_name,
            SUM(de.produced) AS produced,
            SUM(de.waste) AS waste
        FROM daily_entries de
        JOIN products p ON de.product_id = p.product_id
        WHERE de.user_id = %s
        GROUP BY p.product_name
        ORDER BY p.product_name;
        """,
        (user_id,),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows
