import os
import re
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

app = Flask(__name__)

# Initialize database connection pool on startup
from models.db import init_connection_pool
try:
    init_connection_pool()
except Exception as e:
    print(f"Warning: Could not initialize connection pool: {e}")

# 1. DEFINE ALLOWED ORIGINS
DEFAULT_ORIGINS = [
    "https://dunkin-demand-intelligence-neil-barots-projects-55b3b305.vercel.app",
    "https://dunkin-demand-intelligence-h7bvxrxzh.vercel.app",
    "https://dunkin-demand-intelligence.vercel.app"
]

VERCEL_PATTERN = re.compile(r"https://dunkin-demand-intelligence(-.*)?\.vercel\.app$")

def is_allowed_origin(origin):
    if not origin:
        return False
    if origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1"):
        return True
    if origin in DEFAULT_ORIGINS or VERCEL_PATTERN.match(origin):
        return True
    return False

# 2. CONFIGURE CORS
# We set origins to a dummy value to avoid the iteration error, 
# then override it in the hook below.
CORS(app, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if is_allowed_origin(origin):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
    return response

# 3. IMPORT ROUTES (Absolute imports)
from routes.products import products_bp
from routes.daily_entry import daily_bp
from routes.auth import auth_bp
from routes.health import health_bp
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
from routes.throwaway_import import throwaway_import_bp
from routes.calendar_events import bp as calendar_events_bp
from routes.daily_production import bp as daily_production_bp
from routes.daily_production_plan import bp as daily_production_plan_bp
from routes.daily_sales import bp as daily_sales_bp
from routes.daily_throwaway import bp as daily_throwaway_bp
from routes.daily_waste import bp as daily_waste_bp
from routes.forecast_final import bp as forecast_final_bp
from routes.forecast_history import bp as forecast_history_bp
from routes.forecast_raw import bp as forecast_raw_bp
from routes.manager_context import bp as manager_context_bp
from routes.users import bp as users_bp

# 4. REGISTER BLUEPRINTS
app.register_blueprint(products_bp, url_prefix="/api/v1/products")
app.register_blueprint(daily_bp, url_prefix="/api/v1/daily")
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(health_bp, url_prefix="/api/v1")
app.register_blueprint(forecast_bp, url_prefix="/api/v1/forecast")
app.register_blueprint(excel_bp, url_prefix="/api/v1/excel")
app.register_blueprint(export_bp, url_prefix="/api/v1/export")
app.register_blueprint(forecast_context_bp, url_prefix="/api/v1/forecast/context")
app.register_blueprint(throwaway_export_bp, url_prefix="/api/v1/throwaway")
app.register_blueprint(throwaway_import_bp, url_prefix="/api/v1/throwaway")
app.register_blueprint(forecast_v1_bp, url_prefix="/api/v1")
app.register_blueprint(forecast_accuracy_bp, url_prefix="/api/v1/forecast/accuracy")
app.register_blueprint(forecast_learning_bp, url_prefix="/api/v1/forecast/learning")
app.register_blueprint(forecast_approval_bp, url_prefix="/api/v1/forecast/approvals")
app.register_blueprint(waste_submission_bp, url_prefix="/api/v1/waste_submission")
app.register_blueprint(dashboard_bp, url_prefix="/api/v1/dashboard")
app.register_blueprint(system_health_bp, url_prefix="/api/v1")
app.register_blueprint(qr_bp, url_prefix="/api/v1/qr")

# Table route blueprints
app.register_blueprint(calendar_events_bp, url_prefix="/api/v1/calendar_events")
app.register_blueprint(daily_production_bp, url_prefix="/api/v1/daily_production")
app.register_blueprint(daily_production_plan_bp, url_prefix="/api/v1/daily_production_plan")
app.register_blueprint(daily_sales_bp, url_prefix="/api/v1/daily_sales")
app.register_blueprint(daily_throwaway_bp, url_prefix="/api/v1/daily_throwaway")
app.register_blueprint(daily_waste_bp, url_prefix="/api/v1/daily_waste")
app.register_blueprint(forecast_final_bp, url_prefix="/api/v1/forecast_final")
app.register_blueprint(forecast_history_bp, url_prefix="/api/v1/forecast_history")
app.register_blueprint(forecast_raw_bp, url_prefix="/api/v1/forecast_raw")
app.register_blueprint(manager_context_bp, url_prefix="/api/v1/manager_context")
app.register_blueprint(users_bp, url_prefix="/api/v1/users")

@app.get("/")
def home():
    return {"message": "Backend is live"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)