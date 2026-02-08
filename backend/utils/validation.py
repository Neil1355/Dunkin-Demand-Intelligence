"""JSON Schema validation helper for Flask routes.

Usage:
    from backend.utils.validation import validate_json
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
        return jsonify({"status": "error", "message": f"Validation error: {e.message}"}), 400

    return payload
