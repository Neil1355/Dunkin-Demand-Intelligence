from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.daily import daily_bp
from routes.products import products_bp
from routes.forecast import forecast_bp
from models.db import seed_default_products

seed_default_products()

app = Flask(__name__)
CORS(app)

# register blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(daily_bp, url_prefix="/api")
app.register_blueprint(products_bp, url_prefix="/api")
app.register_blueprint(forecast_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)

    