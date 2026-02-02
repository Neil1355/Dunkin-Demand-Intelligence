from statistics import mean

def apply_learning(cur, store_id, product_id, base_qty):
    cur.execute("""
        SELECT avg_error_pct
        FROM forecast_learning
        WHERE store_id = %s AND product_id = %s;
    """, (store_id, product_id))

    row = cur.fetchone()
    if not row:
        return base_qty, 0

    adj = int(base_qty * row["avg_error_pct"])
    return max(0, base_qty + adj), adj

def generate_forecast(cur, store_id, target_date, expectation):

    CONTEXT_MULTIPLIERS = {
        "busy": 1.15,
        "normal": 1.0,
        "slow": 0.85,
        "unsure": 1.0
    }

    multiplier = CONTEXT_MULTIPLIERS.get(expectation, 1.0)

    weekday = target_date.weekday()  # Monday = 0

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

        # Fetch last 9 matching weekdays
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

        adjusted_avg = avg_sold * multiplier

        # 5% safety buffer
        recommended = round(adjusted_avg * 1.05)

        final_qty, learning_adj = apply_learning(
         cur,
         store_id,
         product_id,
         recommended
        )

        forecasts.append({
            "product_id": product_id,
            "product_name": product_name,
            "predicted_quantity": final_qty,
            "adjusted_quantity": final_qty,  
            "learning_adjustment": learning_adj,
            "adjustment_reason": "recent bias correction" if learning_adj != 0 else None,
            "avg_sold": round(avg_sold, 1),
            "confidence": confidence,
            "expectation": expectation,
            "multiplier_used": multiplier
        })

    return forecasts

