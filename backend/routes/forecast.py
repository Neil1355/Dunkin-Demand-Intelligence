from flask import Blueprint, jsonify, request
from backend.models.daily_data_model import get_last_7_days

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/")
def get_forecast():
    user_id = request.args.get("user_id", type=int)

    last_7 = get_last_7_days(user_id)

    if not last_7:
        return jsonify({"forecast": {}, "message": "Not enough data"})

    forecast = {}

    for row in last_7:
        name = row["product_name"]
        waste = row["waste"]

        # naive placeholder: reduce waste by 10%
        forecast[name] = max(int(waste * 0.9), 0)

    return jsonify({"forecast": forecast})
