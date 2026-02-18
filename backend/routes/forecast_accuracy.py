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
from models.db import get_connection, return_connection
from services.forecast_accuracy import compute_forecast_accuracy

forecast_accuracy_bp = Blueprint("forecast_accuracy", __name__)

@forecast_accuracy_bp.route("", methods=["GET"])
def get_accuracy_metrics():
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Compute MAE (Mean Absolute Error)
        cur.execute("SELECT AVG(ABS(error_pct)) FROM forecast_history WHERE error_pct IS NOT NULL")
        mae_row = cur.fetchone()
        mae = mae_row[0] if mae_row[0] else 0

        # Compute MAPE (Mean Absolute Percentage Error) - assuming error_pct is already percentage
        cur.execute("SELECT AVG(ABS(error_pct)) FROM forecast_history WHERE error_pct IS NOT NULL")
        mape = mae  # if error_pct is percentage

        # Bias
        cur.execute("SELECT AVG(error_pct) FROM forecast_history WHERE error_pct IS NOT NULL")
        bias_row = cur.fetchone()
        bias = bias_row[0] if bias_row[0] else 0

        # Last updated
        cur.execute("SELECT MAX(target_date) FROM forecast_history")
        last_row = cur.fetchone()
        last_updated = str(last_row[0]) if last_row[0] else None

        cur.close()

        return jsonify({
            "mae": mae,
            "mape": mape,
            "bias": bias,
            "last_updated": last_updated
        })
    finally:
        return_connection(conn)

@forecast_accuracy_bp.route("/compute", methods=["POST"])
def compute_accuracy_route():
    data = request.json
    store_id = data.get("store_id")
    target_date = data.get("target_date")

    if not store_id or not target_date:
        return jsonify({"error": "store_id and target_date required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        compute_forecast_accuracy(cur, store_id, target_date)

        conn.commit()
        cur.close()

        return jsonify({"message": "Forecast accuracy computed"})
    finally:
        return_connection(conn)
