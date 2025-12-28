from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    return {"message": "Flask is working with blueprints!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)