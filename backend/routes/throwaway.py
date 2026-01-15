from flask import Blueprint, send_file
from backend.models.db import get_connection
import pandas as pd
from io import BytesIO
from datetime import date, timedelta

throwaway_bp = Blueprint("throwaway", __name__, url_prefix="/throwaway")

@throwaway_bp.get("/export")
def export_throwaway_excel():
    store_id = 1  # can parameterize later

    today = date.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)

    conn = get_connection()

    df = pd.read_sql("""
        SELECT
            dt.throwaway_date AS date,
            p.product_name,
            dt.quantity_thrown
        FROM daily_throwaway dt
        JOIN products p ON dt.product_id = p.product_id
        WHERE dt.store_id = %s
          AND dt.throwaway_date >= %s
        ORDER BY dt.throwaway_date;
    """, conn, params=(store_id, last_sunday))

    conn.close()

    if df.empty:
        return {"message": "No data for this week"}, 404

    pivot = df.pivot(
        index="date",
        columns="product_name",
        values="quantity_thrown"
    ).fillna(0).reset_index()

    output = BytesIO()
    pivot.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Weekly_Throwaway.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
