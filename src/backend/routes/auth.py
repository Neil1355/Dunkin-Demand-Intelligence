from flask import Blueprint, request, jsonify
from backend.models.user_model import create_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/signup")
def signup():
    data = request.json
    result = create_user(data["name"], data["email"], data["password"])
    return jsonify(result)

@auth_bp.post("/login")
def login():
    data = request.json
    result = authenticate_user(data["email"], data["password"])
    return jsonify(result)
