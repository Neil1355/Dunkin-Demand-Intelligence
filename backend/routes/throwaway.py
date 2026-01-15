from flask import Blueprint, request, jsonify
from backend.models.db import get_connection

throwaway_bp = Blueprint("throwaway", __name__, url_prefix="/throwaway")

@throwaway_bp.post("/upload")
def upload_throwaway():
    data = request.get_json()

    store_id = data.get("store_id")
    throwaway_date = data.get("throwaway_date")
    items = data.get("items", [])

    if not store_id or not throwaway_date or not items:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cur = conn.cursor()

    try:
        for item in items:
            cur.execute(
                """
                INSERT INTO daily_throwaway (store_id, product_id, throwaway_date, quantity_thrown)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, throwaway_date, product_id)
                DO UPDATE SET quantity_thrown = EXCLUDED.quantity_thrown
                """,
                (
                    store_id,
                    item["product_id"],
                    throwaway_date,
                    item["quantity_thrown"]
                )
            )

        conn.commit()
        return jsonify({"message": "Throwaway data saved successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()