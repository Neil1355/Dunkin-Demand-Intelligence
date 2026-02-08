"""
⚠️ WARNING
This file contains production business logic.

DO NOT:
- Move logic to frontend
- Recompute models on request
- Change field names without updating API_CONTRACT.md

Read-only or controlled writes only.
"""
from flask import Blueprint, request, jsonify
from datetime import date, timedelta
from models.db import get_connection
from services.forecast_engine import generate_forecast
from services.context_adjuster import apply_context_adjustment
print("DEBUG: forecast_v1 loaded with target_date parsing")
forecast_v1_bp = Blueprint("forecast_v1", __name__)

@forecast_v1_bp.route("/forecast", methods=["GET"])
def get_forecast():
    store_id = request.args.get("store_id", type=int)
    target_date = request.args.get("target_date", type=str)
    if not store_id or not target_date:
        return jsonify({"error": "store_id and target_date required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            fh.product_id,
            p.product_name,
            fh.predicted_quantity,
            fh.adjusted_quantity,
            fh.final_quantity,
            fh.status,
            fh.model_version
        FROM forecast_history fh
        JOIN products p ON p.product_id = fh.product_id
        WHERE fh.store_id = %s
          AND fh.target_date = %s
        ORDER BY p.product_name
    """, (store_id, target_date))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return jsonify({"error": "No forecast found"}), 404

    products = []
    for row in rows:
        products.append({
            "product_id": row[0],
            "product_name": row[1],
            "predicted_quantity": row[2],
            "adjusted_quantity": row[3],
            "final_quantity": row[4],
            "status": row[5],
            "model_version": row[6]
        })

    return jsonify({
        "store_id": store_id,
        "target_date": target_date,
        "products": products
    })

@forecast_v1_bp.route("/forecast/history", methods=["GET"])
def get_forecast_history():
    limit = request.args.get("limit", type=int, default=30)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            target_date,
            SUM(predicted_quantity) as total_predicted,
            SUM(final_quantity) as total_final,
            AVG(error_pct) as avg_error
        FROM forecast_history
        WHERE target_date <= CURRENT_DATE
        GROUP BY target_date
        ORDER BY target_date DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "target_date": str(row[0]),
            "total_predicted": row[1],
            "total_final": row[2],
            "avg_error": row[3]
        })

    return jsonify(history)
