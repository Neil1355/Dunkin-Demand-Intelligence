from flask import Blueprint, request, jsonify
from datetime import date, timedelta
from backend.models.db import get_connection
from backend.services.forecast_engine import generate_forecast

forecast_v1_bp = Blueprint("forecast_v1", __name__)

@forecast_v1_bp.route("/v1", methods=["GET"])
def forecast_v1():
    store_id = request.args.get("store_id", type=int)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    target_date = date.today() + timedelta(days=1)

    conn = get_connection()
    cur = conn.cursor()

    forecasts = generate_forecast(cur, store_id, target_date)

    # log forecast history
    for f in forecasts:
        cur.execute("""
             INSERT INTO public.forecast_history
             (store_id, product_id, forecast_date, target_date, predicted_quantity, model_version)
             VALUES (%s, %s, %s, %s, %s, 'v1_weekday_avg')
        """, (
            store_id,
            f["product_id"],
            date.today(),       # when forecast was generated
            target_date,        # the day being predicted
            f["recommended_production"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "store_id": store_id,
        "forecast_date": str(target_date),
        "model": "v1_weekday_avg",
        "products": forecasts
    })
