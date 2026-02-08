from flask import Blueprint, request, jsonify, abort
from models.user_model import create_user, authenticate_user
from backend.utils.validation import validate_json

# JSON schema for signup/login
signup_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 6}
    },
    "required": ["name", "email", "password"],
    "additionalProperties": False,
}

login_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 6}
    },
    "required": ["email", "password"],
    "additionalProperties": False,
}

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    validated = validate_json(request, signup_schema)
    if isinstance(validated, tuple):
        return validated

    name = validated.get("name")
    email = validated.get("email")
    password = validated.get("password")

    result = create_user(name, email, password)
    return jsonify(result), 201


@auth_bp.post("/login")
def login():
    validated = validate_json(request, login_schema)
    if isinstance(validated, tuple):
        return validated

    email = validated.get("email")
    password = validated.get("password")

    result = authenticate_user(email, password)
    if result.get("status") != "success":
        return jsonify(result), 401
    return jsonify(result), 200
