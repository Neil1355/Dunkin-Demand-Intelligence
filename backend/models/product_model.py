from .db import get_connection
from psycopg2.extras import RealDictCursor

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT product_id, product_name, product_type, is_active
        FROM public.products
        ORDER BY product_type, product_name
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
