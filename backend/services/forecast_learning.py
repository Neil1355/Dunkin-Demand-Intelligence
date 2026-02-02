from datetime import date, timedelta

LOOKBACK_DAYS = 7
MAX_ADJUSTMENT_PCT = 0.15  # ±15% cap

def update_learning(cur, store_id):
    since = date.today() - timedelta(days=LOOKBACK_DAYS)

    cur.execute("""
        SELECT
            product_id,
            AVG(forecast_error) AS avg_error,
            AVG(error_pct) AS avg_error_pct,
            COUNT(*) AS n
        FROM forecast_history
        WHERE store_id = %s
          AND status = 'approved'
          AND target_date >= %s
          AND actual_sold IS NOT NULL
        GROUP BY product_id;
    """, (store_id, since))

    rows = cur.fetchall()

    for r in rows:
        adj_pct = max(
            -MAX_ADJUSTMENT_PCT,
            min(MAX_ADJUSTMENT_PCT, r["avg_error_pct"])
        )

        cur.execute("""
            INSERT INTO forecast_learning
            (store_id, product_id, avg_error, avg_error_pct, sample_size, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (store_id, product_id)
            DO UPDATE SET
                avg_error = EXCLUDED.avg_error,
                avg_error_pct = EXCLUDED.avg_error_pct,
                sample_size = EXCLUDED.sample_size,
                last_updated = EXCLUDED.last_updated;
        """, (
            store_id,
            r["product_id"],
            r["avg_error"],
            adj_pct,
            r["n"],
            date.today()
        ))
