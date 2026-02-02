from flask import Blueprint, jsonify
from backend.models.db import get_connection

system_health_bp = Blueprint("system_health", __name__)

@system_health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "version": "v1",
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "unreachable",
            "error": str(e)
        }), 500