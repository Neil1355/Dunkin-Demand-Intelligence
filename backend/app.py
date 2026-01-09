import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Allow frontend (Vercel) to call backend
CORS(
    app,
    resources={r"/*": {"origins": "*"}},  # later we will restrict this
    supports_credentials=True
)

from backend.routes.products import products_bp
from backend.routes.daily import daily_bp
from backend.routes.auth import auth_bp
from backend.routes.forecast import forecast_bp

app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(daily_bp, url_prefix="/daily")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(forecast_bp, url_prefix="/forecast")

@app.get("/")
def home():
    return {"message": "Backend is live"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
