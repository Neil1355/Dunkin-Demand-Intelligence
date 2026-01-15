from flask import Blueprint, jsonify, request
from backend.models.daily_data_model import get_last_7_days

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/")
def get_forecast():
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    last_7 = get_last_7_days(user_id)

    if len(last_7) < 3:
        return jsonify({"forecast": {}, "message": "Not enough data"})

    forecast = {}

    for row in last_7:
        name = row["product_name"]
        produced = row["produced"]
        waste = row["waste"]

        net = max(produced - waste, 0)

        if name not in forecast:
            forecast[name] = []

        forecast[name].append(net)

    # average net sales → tomorrow’s production
    final_forecast = {
        name: max(int(sum(values) / len(values) * 1.05), 1)
        for name, values in forecast.items()
    }

    return jsonify({"forecast": final_forecast})
