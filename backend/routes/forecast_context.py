from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection

forecast_context_bp = Blueprint("forecast_context", __name__)


def normalize_expectation(raw_expectation: str | None) -> str:
    """Map UI values to DB-allowed expectation values."""
    if not raw_expectation:
        return "unsure"

    normalized = raw_expectation.strip().lower()
    mapping = {
        "yes": "busy",
        "busy": "busy",
        "no": "slow",
        "slow": "slow",
        "slower": "slow",
        "maybe": "unsure",
        "not_sure": "unsure",
        "unsure": "unsure",
        "normal": "normal",
    }
    return mapping.get(normalized, "unsure")

@forecast_context_bp.post("/")
def save_forecast_context():
    data = request.get_json()

    store_id = data.get("store_id")
    target_date = data.get("target_date")
    expectation = normalize_expectation(data.get("expectation"))
    reason = data.get("reason")
    notes = data.get("notes")

    if not all([store_id, target_date, expectation]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO public.forecast_context
            (store_id, target_date, expectation, reason, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (store_id, target_date)
            DO UPDATE SET
              expectation = EXCLUDED.expectation,
              reason = EXCLUDED.reason,
              notes = EXCLUDED.notes;
        """, (store_id, target_date, expectation, reason, notes))

        conn.commit()
        cur.close()

        return jsonify({"message": "Forecast context saved"}), 201
    finally:
        return_connection(conn)
