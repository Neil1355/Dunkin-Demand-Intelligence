"""JSON Schema validation helper for Flask routes.

Usage:
    from utils.validation import validate_json
    @bp.route('/', methods=['POST'])
    def create():
        payload = validate_json(request, schema)
        if isinstance(payload, tuple):
            return payload  # error response
        ...
"""
from jsonschema import validate, ValidationError
from flask import jsonify


def validate_json(request, schema):
    try:
        payload = request.get_json() or {}
    except Exception:
        return jsonify({"status": "error", "message": "Invalid JSON body"}), 400

    try:
        validate(instance=payload, schema=schema)
    except ValidationError as e:
        # Provide user-friendly error messages
        error_msg = e.message
        if "is too short" in error_msg:
            field_name = e.path[0] if e.path else "Field"
            if "''" in error_msg or "is too short" in error_msg:
                error_msg = f"{field_name.capitalize()} is required"
        elif "format" in error_msg:
            error_msg = "Please enter a valid email address"
        return jsonify({"status": "error", "message": error_msg}), 400

    return payload
