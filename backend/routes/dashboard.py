from flask import Blueprint, request, jsonify
from ..models.db import get_connection
from datetime import date, timedelta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/daily", methods=["GET"])
def daily_snapshot():
    store_id = request.args.get("store_id", type=int)
    target_date = request.args.get("date")

    if not store_id or not target_date:
        return jsonify({"error": "store_id and date required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.product_name,
            fh.predicted_quantity,
            fh.final_quantity,
            fh.actual_sold,
            ws.waste_quantity,
            fh.error_pct
        FROM forecast_history fh
        JOIN products p ON p.product_id = fh.product_id
        LEFT JOIN waste_submissions ws
            ON ws.store_id = fh.store_id
           AND ws.product_id = fh.product_id
           AND ws.waste_date = fh.target_date
        WHERE fh.store_id = %s
          AND fh.target_date = %s
        ORDER BY p.product_name;
    """, (store_id, target_date))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@dashboard_bp.route("/accuracy", methods=["GET"])
def accuracy_trend():
    store_id = request.args.get("store_id", type=int)
    days = request.args.get("days", type=int, default=14)

    since = date.today() - timedelta(days=days)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            target_date,
            AVG(error_pct) AS avg_error_pct
        FROM forecast_history
        WHERE store_id = %s
          AND status = 'approved'
          AND target_date >= %s
        GROUP BY target_date
        ORDER BY target_date;
    """, (store_id, since))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@dashboard_bp.route("/learning", methods=["GET"])
def learning_status():
    store_id = request.args.get("store_id", type=int)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.product_name,
            fl.avg_error_pct,
            fl.sample_size,
            fl.last_updated
        FROM forecast_learning fl
        JOIN products p ON p.product_id = fl.product_id
        WHERE fl.store_id = %s
        ORDER BY p.product_name;
    """, (store_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)
