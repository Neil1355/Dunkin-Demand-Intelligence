from flask import Blueprint, request, jsonify
from backend.models.daily_data_model import get_last_7_days

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/")
def get_forecast():
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    rows = get_last_7_days(user_id)

    if not rows:
        return jsonify({"forecast": {}, "message": "Not enough data"})

    forecast = {}

    for row in rows:
        name = row["product_name"]
        waste = row["waste"]

        # naive forecast: reduce waste by 10%
        forecast[name] = max(int(waste * 0.9), 0)

    return jsonify({"forecast": forecast})
