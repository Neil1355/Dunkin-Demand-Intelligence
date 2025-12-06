from flask import Blueprint, jsonify, request
from backend.models.daily_data_model import get_last_7_days

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/")
def get_forecast():
    """
    Simple placeholder forecast based on last 7 days.
    We'll replace this with real ML later.
    """

    last_7 = get_last_7_days()

    if not last_7:
        return jsonify({"forecast": {}, "message": "Not enough data"})

    forecast = {}

    for row in last_7:
        name = row["item_name"]
        produced = row["produced"]
        waste = row["waste"]

        # Simple rule-based estimate: reduce waste 10%
        forecast[name] = int(produced - (waste * 0.1))

    return jsonify({"forecast": forecast})
