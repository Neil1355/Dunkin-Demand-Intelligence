import os
from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

print("DATABASE_URL LOADED:", os.getenv("DATABASE_URL"))


app = Flask(__name__)

# Allow frontend (Vercel) to call backend
CORS(
    app,
    resources={r"/*": {"origins": "*"}},  # later we will restrict this
    supports_credentials=True
)

from routes.products import products_bp
from routes.daily_entry import daily_bp
from routes.auth import auth_bp
from routes.forecast import forecast_bp
from services.excel_import import excel_bp
from routes.export import export_bp
from routes.forecast_context import forecast_context_bp
from routes.throwaway_export import throwaway_export_bp
from routes.forecast_v1 import forecast_v1_bp
from routes.forecast_approval import forecast_approval_bp
from routes.waste_submission import waste_submission_bp
from routes.forecast_accuracy import forecast_accuracy_bp
from routes.forecast_learning import forecast_learning_bp
from routes.qr import qr_bp
from routes.dashboard import dashboard_bp
from routes.system_health import system_health_bp

app.register_blueprint(products_bp, url_prefix="/api/v1/products")
app.register_blueprint(daily_bp, url_prefix="/api/v1/daily")
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(forecast_bp, url_prefix="/api/v1/forecast")
app.register_blueprint(excel_bp, url_prefix="/api/v1/excel")
app.register_blueprint(export_bp, url_prefix="/api/v1/export")
app.register_blueprint(forecast_context_bp, url_prefix="/api/v1/forecast/context")
app.register_blueprint(throwaway_export_bp, url_prefix="/api/v1/throwaway")
app.register_blueprint(forecast_v1_bp, url_prefix="/api/v1")
app.register_blueprint(forecast_accuracy_bp, url_prefix="/api/v1/forecast/accuracy")
app.register_blueprint(forecast_learning_bp, url_prefix="/api/v1/forecast/learning")
app.register_blueprint(forecast_approval_bp, url_prefix="/api/v1/forecast/approvals")
app.register_blueprint(dashboard_bp, url_prefix="/api/v1/dashboard")
app.register_blueprint(system_health_bp, url_prefix="/api/v1")


@app.get("/")
def home():
    return {"message": "Backend is live"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
