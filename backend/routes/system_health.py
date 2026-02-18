from flask import Blueprint, jsonify
from models.db import get_connection, return_connection

system_health_bp = Blueprint("system_health", __name__)

@system_health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.fetchone()
            cur.close()

            return jsonify({
                "status": "ok",
                "database": "connected",
                "version": "v1",
            })
        finally:
            return_connection(conn)

    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "unreachable",
            "error": str(e)
        }), 500
