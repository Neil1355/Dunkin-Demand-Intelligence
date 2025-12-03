from flask import Blueprint, request, jsonify
from backend.models.daily_data_model import insert_daily_entry

daily_bp = Blueprint('daily', __name__)

@daily_bp.post("/submit")
def save_daily_data():
    data = request.json

    for item in data["items"]:
        insert_daily_entry(
            data["user_id"],
            item["product_id"],
            data["date"],
            item["produced"],
            item["wasted"]
        )

    return jsonify({"status": "success"})
