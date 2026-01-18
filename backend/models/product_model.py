from backend.models.db import get_connection

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT product_id, product_name, product_type, is_active
        FROM public.products
        ORDER BY product_type, product_name
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows