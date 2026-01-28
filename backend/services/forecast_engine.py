from statistics import mean, stdev

def generate_forecast(cur, store_id, target_date):
    weekday = target_date.weekday()  # Monday=0

    cur.execute("""
        SELECT product_id, product_name
        FROM public.products
        WHERE is_active = TRUE
    """)
    products = cur.fetchall()

    forecasts = []

    for p in products:
        product_id = p["product_id"]
        product_name = p["product_name"]

        cur.execute("""
            SELECT
              produced,
              waste,
              (produced - waste) AS sold
            FROM public.daily_throwaway
            WHERE store_id = %s
              AND product_id = %s
              AND EXTRACT(DOW FROM date) = %s
              AND produced IS NOT NULL
              AND waste IS NOT NULL
            ORDER BY date DESC
            LIMIT 9;
        """, (store_id, product_id, weekday))

        rows = cur.fetchall()
        if len(rows) == 0:
            continue

        sold_values = [r["sold"] for r in rows]
        avg_sold = mean(sold_values)
        count = len(sold_values)

        confidence = (
            "high" if count >= 6 else
            "medium" if count >= 4 else
            "low"
        )

        recommended = round(avg_sold * 1.05)

        forecasts.append({
            "product_id": product_id,
            "product_name": product_name,
            "recommended_production": recommended,
            "avg_sold": round(avg_sold, 1),
            "confidence": confidence
        })

    return forecasts
