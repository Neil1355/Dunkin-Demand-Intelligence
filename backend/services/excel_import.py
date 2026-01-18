from flask import Blueprint, request, jsonify
import pandas as pd
from backend.models.db import get_connection

excel_bp = Blueprint("excel", __name__, url_prefix="/excel")

@excel_bp.post("/upload")
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    df = pd.read_excel(file)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"store_id", "product_id", "date"}
    if not required.issubset(df.columns):
        return jsonify({"error": "Missing required columns"}), 400

    conn = get_connection()
    cur = conn.cursor()

    inserted = 0

    try:
        for _, row in df.iterrows():
            store_id = int(row["store_id"])
            product_id = int(row["product_id"])
            date = row["date"]

            produced = int(row.get("produced", 0) or 0)
            waste = int(row.get("waste", 0) or 0)

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

            inserted += 1

        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "message": "Excel uploaded successfully",
        "rows_processed": inserted
    })
