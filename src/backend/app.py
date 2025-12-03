from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import routes AFTER app and AFTER __init__.py exists
from backend.routes.daily import daily_bp

# Register blueprints
app.register_blueprint(daily_bp, url_prefix="/daily")

@app.get("/")
def home():
    return {"message": "Flask is working with blueprints!"}

if __name__ == "__main__":
    app.run(debug=True)
