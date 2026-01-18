from flask import Blueprint, request, jsonify
from backend.models.db import get_connection

daily_bp = Blueprint("daily", __name__)

@daily_bp.route("/daily", methods=["POST"])
def upload_daily():
    data = request.get_json()

    store_id = data.get("store_id")
    product_id = data.get("product_id")
    date = data.get("date")
    produced = data.get("produced", 0)
    waste = data.get("waste", 0)

    if not all([store_id, product_id, date]):
        return jsonify({"error": "store_id, product_id, date required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    try:
        if produced > 0:
            cur.execute("""
                INSERT INTO public.daily_production
                (store_id, product_id, production_date, quantity_produced)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, production_date)
                DO UPDATE SET quantity_produced = EXCLUDED.quantity_produced
            """, (store_id, product_id, date, produced))

        if waste > 0:
            cur.execute("""
                INSERT INTO public.daily_throwaway
                (store_id, product_id, throwaway_date, quantity_thrown)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, throwaway_date)
                DO UPDATE SET quantity_thrown = EXCLUDED.quantity_thrown
            """, (store_id, product_id, date, waste))

        conn.commit()
        return jsonify({"message": "Daily data saved"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
