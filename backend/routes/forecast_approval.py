from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection
from datetime import datetime

forecast_approval_bp = Blueprint("forecast_approval", __name__)

@forecast_approval_bp.route("", methods=["GET"])
def get_approvals():
    store_id = request.args.get("store_id", type=int)
    status = request.args.get("status", default="pending")

    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                fh.product_id,
                p.product_name,
                fh.predicted_quantity,
                fh.adjusted_quantity,
                fh.final_quantity,
                fh.status
            FROM forecast_history fh
            JOIN products p ON p.product_id = fh.product_id
            WHERE fh.store_id = %s
              AND fh.status = %s
            ORDER BY p.product_name;
        """, (store_id, status))

        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)
    finally:
        return_connection(conn)

@forecast_approval_bp.route("/pending", methods=["GET"])
def get_pending_forecasts():
    store_id = request.args.get("store_id", type=int)
    target_date = request.args.get("target_date")

    if not store_id or not target_date:
        return jsonify({"error": "store_id and target_date required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                fh.product_id,
                p.product_name,
                fh.predicted_quantity,
                fh.adjusted_quantity,
                fh.final_quantity,
                fh.status
            FROM forecast_history fh
            JOIN products p ON p.product_id = fh.product_id
            WHERE fh.store_id = %s
              AND fh.target_date = %s
              AND fh.status = 'pending'
            ORDER BY p.product_name;
        """, (store_id, target_date))

        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)
    finally:
        return_connection(conn)


@forecast_approval_bp.route("/approve", methods=["POST"])
def approve_forecast():
    data = request.json

    store_id = data.get("store_id")
    target_date = data.get("target_date")
    approved_by = data.get("approved_by")
    updates = data.get("updates")

    if not all([store_id, target_date, approved_by, updates]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        for item in updates:
            cur.execute("""
                UPDATE forecast_history
                SET
                    final_quantity = %s,
                    status = 'approved',
                    approved_by = %s,
                    approved_at = %s
                WHERE store_id = %s
                  AND product_id = %s
                  AND target_date = %s;
            """, (
                item["final_quantity"],
                approved_by,
                datetime.utcnow(),
                store_id,
                item["product_id"],
                target_date
            ))

        conn.commit()
        cur.close()

        return jsonify({"message": "Forecast approved"})
    finally:
        return_connection(conn)
