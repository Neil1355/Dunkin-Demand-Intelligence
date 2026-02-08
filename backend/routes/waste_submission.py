from datetime import date
from flask import Blueprint, request, jsonify
from models.db import get_connection
from services.forecast_accuracy import compute_forecast_accuracy
waste_submission_bp = Blueprint("waste_submission", __name__)

@waste_submission_bp.route("/submit", methods=["POST"])
def submit_waste():
    data = request.json
    store_id = data.get("store_id")
    submitted_by = data.get("submitted_by")
    entries = data.get("entries")  # [{product_id, waste_quantity}]

    if not all([store_id, submitted_by, entries]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    cur = conn.cursor()

    for e in entries:
        cur.execute("""
            INSERT INTO waste_submissions
            (store_id, product_id, submission_date, waste_quantity, submitted_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            store_id,
            e["product_id"],
            date.today(),
            e["waste_quantity"],
            submitted_by
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Waste submitted for approval"})

@waste_submission_bp.route("/pending", methods=["GET"])
def get_pending_waste():
    store_id = request.args.get("store_id", type=int)
    waste_date = request.args.get("waste_date")

    if not store_id or not waste_date:
        return jsonify({"error": "store_id and waste_date required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ws.submission_id,
            ws.product_id,
            p.product_name,
            ws.waste_quantity,
            ws.submitted_by,
            ws.created_at
        FROM waste_submissions ws
        JOIN products p ON p.product_id = ws.product_id
        WHERE ws.store_id = %s
          AND ws.waste_date = %s
          AND ws.status = 'pending'
        ORDER BY p.product_name;
    """, (store_id, waste_date))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

from flask import Blueprint, request, jsonify
from models.db import get_connection
from datetime import date

# 1. DEFINE BLUEPRINT FIRST
waste_submission_bp = Blueprint("waste_submission", __name__)

# ---------------------------------------------------------
# 1. Staff submits waste
# ---------------------------------------------------------
@waste_submission_bp.route("/submit", methods=["POST"])
def submit_waste():
    data = request.json

    store_id = data.get("store_id")
    submitted_by = data.get("submitted_by")
    waste_date = data.get("waste_date", str(date.today()))
    entries = data.get("entries")

    if not all([store_id, submitted_by, entries]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cur = conn.cursor()

    for item in entries:
        cur.execute("""
            INSERT INTO waste_submissions
            (store_id, product_id, waste_date, waste_quantity, submitted_by)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (store_id, product_id, waste_date)
            DO UPDATE SET
                waste_quantity = EXCLUDED.waste_quantity,
                submitted_by = EXCLUDED.submitted_by,
                status = 'pending';
        """, (
            store_id,
            item["product_id"],
            waste_date,
            item["waste_quantity"],
            submitted_by
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Waste submitted for approval"})

# ---------------------------------------------------------
# 2. Manager views pending waste
# ---------------------------------------------------------
@waste_submission_bp.route("/pending", methods=["GET"])
def pending_waste():
    store_id = request.args.get("store_id", type=int)
    waste_date = request.args.get("waste_date")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ws.submission_id,
            ws.product_id,
            p.product_name,
            ws.waste_quantity,
            ws.submitted_by
        FROM waste_submissions ws
        JOIN products p ON p.product_id = ws.product_id
        WHERE ws.store_id = %s
          AND ws.waste_date = %s
          AND ws.status = 'pending'
        ORDER BY p.product_name;
    """, (store_id, waste_date))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)


# ---------------------------------------------------------
# 3. Manager approves waste
# ---------------------------------------------------------
@waste_submission_bp.route("/approve", methods=["POST"])
def approve_waste():
    data = request.json

    store_id = data.get("store_id")
    waste_date = data.get("waste_date")
    approved_by = data.get("approved_by")
    submission_ids = data.get("submission_ids")

    if not all([store_id, waste_date, approved_by, submission_ids]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cur = conn.cursor()

    for sid in submission_ids:
        cur.execute("""
            UPDATE waste_submissions
            SET status = 'approved',
                approved_by = %s,
                approved_at = now()
            WHERE submission_id = %s
            RETURNING product_id, waste_quantity;
        """, (approved_by, sid))

        row = cur.fetchone()
        if row:
            product_id, waste_qty = row

            cur.execute("""
                INSERT INTO daily_throwaway
                (store_id, product_id, date, waste)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, date)
                DO UPDATE SET waste = EXCLUDED.waste;
            """, (
                store_id,
                product_id,
                waste_date,
                waste_qty
            ))
    compute_forecast_accuracy(cur, store_id, waste_date)



    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Waste approved and recorded"})
