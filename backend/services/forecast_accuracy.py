def compute_forecast_accuracy(cur, store_id, target_date):
    cur.execute("""
        SELECT
            dp.product_id,
            dp.planned_quantity,
            dt.produced,
            dt.waste
        FROM daily_production_plan dp
        JOIN daily_throwaway dt
          ON dp.store_id = dt.store_id
         AND dp.product_id = dt.product_id
         AND dp.production_date = dt.date
        WHERE dp.store_id = %s
          AND dp.production_date = %s;
    """, (store_id, target_date))

    rows = cur.fetchall()

    for r in rows:
        sold = r["produced"] - r["waste"]
        error_qty = sold - r["planned_quantity"]

        error_pct = (
            (error_qty / r["planned_quantity"]) * 100
            if r["planned_quantity"] > 0 else 0
        )

        cur.execute("""
            INSERT INTO forecast_accuracy
            (store_id, product_id, target_date,
             planned_quantity, actual_produced,
             actual_sold, actual_waste,
             error_quantity, error_percent)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (store_id, product_id, target_date)
            DO UPDATE SET
              actual_produced = EXCLUDED.actual_produced,
              actual_sold = EXCLUDED.actual_sold,
              actual_waste = EXCLUDED.actual_waste,
              error_quantity = EXCLUDED.error_quantity,
              error_percent = EXCLUDED.error_percent,
              created_at = now();
        """, (
            store_id,
            r["product_id"],
            target_date,
            r["planned_quantity"],
            r["produced"],
            sold,
            r["waste"],
            error_qty,
            error_pct
        ))