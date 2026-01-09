from flask import Blueprint, jsonify, request
from backend.models.daily_data_model import get_last_7_days

forecast_bp = Blueprint("forecast", __name__)

@forecast_bp.get("/")
def get_forecast():
    """
    Simple placeholder forecast based on last 7 days.
    We'll replace this with real ML later.

    Optional: pass ?user_id=1
    If not provided, we default to user_id=1 for now (MVP).
    """

    user_id = request.args.get("user_id", default=1, type=int)

    last_7 = get_last_7_days(user_id)

    if not last_7:
        return jsonify({"forecast": {}, "message": "Not enough data"})

    forecast = {}

    for row in last_7:
        # NOTE: these keys must match what get_last_7_days returns
        name = row.get("item_name")
        produced = row.get("produced", 0)
        waste = row.get("waste", 0)

        if not name:
            continue

        # Simple rule-based estimate: reduce waste 10%
        forecast[name] = int(produced - (waste * 0.1))

    return jsonify({"forecast": forecast, "user_id": user_id})
