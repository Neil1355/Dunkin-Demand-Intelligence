from flask import Blueprint, request, jsonify
from backend.models.daily_data_model import insert_daily_entry

daily_bp = Blueprint("daily", __name__)

@daily_bp.post("/upload")
def upload_daily():
    data = request.get_json()

    user_id = data.get("user_id")
    product_id = data.get("product_id")
    date = data.get("date")
    produced = data.get("produced")
    waste = data.get("waste")

    if not all([user_id, product_id, date]):
        return jsonify({"error": "Missing required fields"}), 400

    insert_daily_entry(user_id, product_id, date, produced or 0, waste or 0)

    return jsonify({"message": "Daily entry saved"})
