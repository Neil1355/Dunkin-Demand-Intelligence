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
from backend.models.db import get_connection
from backend.services.forecast_learning import update_learning

forecast_learning_bp = Blueprint("forecast_learning", __name__)

@forecast_learning_bp.route("/summary", methods=["GET"])
def get_learning_summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT last_updated, changes FROM forecast_learning ORDER BY last_updated DESC LIMIT 1")
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return jsonify({
            "last_updated": str(row[0]),
            "changes": row[1]
        })
    else:
        return jsonify({
            "last_updated": None,
            "changes": "No learning data available"
        })

@forecast_learning_bp.post("/update")
def update_learning_route():
    data = request.json
    store_id = data.get("store_id")

    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    update_learning(cur, store_id)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Learning updated"})