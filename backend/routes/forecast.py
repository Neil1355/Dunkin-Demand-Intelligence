from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection
from datetime import date, timedelta

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/next-day")
def next_day_forecast():
    store_id = request.args.get("store_id", type=int)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        target_date = request.args.get("target_date", type=lambda d: date.fromisoformat(d)) or (date.today() + timedelta(days=1))
        target_isodow = target_date.isoweekday()

        cur.execute("SELECT product_id FROM products WHERE is_active = TRUE")
        products = cur.fetchall()

        forecast = {}

        for product in products:
            product_id = product["product_id"]

            # Use recent same-weekday performance from imported throwaway sheets.
            # sold ~= produced - waste.
            cur.execute("""
                SELECT
                    GREATEST(COALESCE(dt.produced, 0) - COALESCE(dt.waste, 0), 0) AS sold
                FROM daily_throwaway dt
                WHERE dt.store_id = %s
                  AND dt.product_id = %s
                  AND dt.date < %s
                  AND EXTRACT(ISODOW FROM dt.date) = %s
                ORDER BY dt.date DESC
                LIMIT 4
            """, (store_id, product_id, target_date, target_isodow))

            rows = cur.fetchall()
            if not rows:
                continue

            sold_values = [int(r["sold"] or 0) for r in rows]
            avg_sold = max(int(round(sum(sold_values) / len(sold_values))), 0)

            cur.execute("""
                INSERT INTO forecast_history
                (store_id, product_id, forecast_date, target_date, predicted_quantity, model_version, status)
                VALUES (%s, %s, CURRENT_DATE, %s, %s, 'v1', 'pending')
                ON CONFLICT (store_id, product_id, target_date)
                DO UPDATE SET
                    forecast_date = EXCLUDED.forecast_date,
                    predicted_quantity = EXCLUDED.predicted_quantity,
                    model_version = EXCLUDED.model_version,
                    status = EXCLUDED.status,
                    created_at = NOW();
            """, (store_id, product_id, target_date, avg_sold))

            forecast[product_id] = avg_sold

        conn.commit()
        cur.close()

        return jsonify({
            "store_id": store_id,
            "target_date": str(target_date),
            "forecast": forecast
        })
    finally:
        return_connection(conn)
