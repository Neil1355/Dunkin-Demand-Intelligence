from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return {"message": "Flask is working!"}


# ----------- DAILY DATA ENDPOINT ----------- #
@app.get("/daily")
def get_daily_data():
    # For now returning mock data (later we connect MySQL here)
    data = {
        "date": "2025-11-27",
        "total_production": 842,
        "total_waste": 52,
        "items": [
            {"name": "glazed", "produced": 120, "waste": 6},
            {"name": "boston creme", "produced": 90, "waste": 5},
        ]
    }
    return jsonify(data)


# ----------- FORECAST ENDPOINT ----------- #
@app.get("/forecast")
def get_forecast():
    # Mock forecast for now (later AI logic goes here)
    forecast = {
        "recommended_total": 798,
        "recommendations": [
            {"name": "glazed", "suggested": 115},
            {"name": "boston creme", "suggested": 95},
        ]
    }
    return jsonify(forecast)


if __name__ == "__main__":
    app.run(debug=True)
