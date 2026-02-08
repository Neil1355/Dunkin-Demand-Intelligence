from flask import Blueprint, request, jsonify
from models.db import get_connection
from datetime import date, timedelta

forecast_bp = Blueprint("forecast", __name__, url_prefix="/forecast")

@forecast_bp.get("/next-day")
def next_day_forecast():
    store_id = request.args.get("store_id", type=int)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    target_date = request.args.get("target_date", type=lambda d: date.fromisoformat(d)) \
              or date.today() + timedelta(days=1)
    weekday = target_date.weekday()

    cur.execute("SELECT product_id FROM products WHERE is_active = true")
    products = cur.fetchall()

    forecast = {}

    for (product_id,) in products:
        cur.execute("""
            SELECT
                p.production_date,
                p.quantity_produced,
                COALESCE(t.quantity_thrown, 0) AS waste
            FROM daily_production p
            LEFT JOIN daily_throwaway t
              ON p.store_id = t.store_id
             AND p.product_id = t.product_id
             AND p.production_date = t.throwaway_date
            WHERE p.store_id = %s
              AND p.product_id = %s
              AND EXTRACT(DOW FROM p.production_date) = %s
            ORDER BY p.production_date DESC
            LIMIT 4
        """, (store_id, product_id, weekday))

        rows = cur.fetchall()
        if not rows:
            continue

        sold = [(r[1] - r[2]) for r in rows]
        avg_sold = max(int(sum(sold) / len(sold)), 0)

        cur.execute("""
            INSERT INTO forecast_history
            (store_id, product_id, forecast_date, target_date, predicted_quantity)
            VALUES (%s, %s, CURRENT_DATE, %s, %s)
        """, (store_id, product_id, target_date, avg_sold))

        forecast[product_id] = avg_sold

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "store_id": store_id,
        "target_date": str(target_date),
        "forecast": forecast
    })
