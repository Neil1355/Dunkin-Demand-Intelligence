from flask import Blueprint, request, send_file, jsonify
import pandas as pd
from datetime import timedelta
from models.db import get_connection
from openpyxl import load_workbook
from openpyxl.styles import Alignment

throwaway_export_bp = Blueprint("throwaway_export", __name__, url_prefix="/throwaway")

@throwaway_export_bp.get("/export")
def export_throwaway():
    store_id = request.args.get("store_id", type=int)
    week_start = request.args.get("week_start")  # YYYY-MM-DD

    if not store_id or not week_start:
        return jsonify({"error": "store_id and week_start required"}), 400

    week_start = pd.to_datetime(week_start).date()
    dates = [week_start + timedelta(days=i) for i in range(7)]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.product_name,
            dt.date,
            dt.produced,
            dt.waste
        FROM daily_throwaway dt
        JOIN products p ON dt.product_id = p.product_id
        WHERE dt.store_id = %s
          AND dt.date BETWEEN %s AND %s
        ORDER BY p.product_name, dt.date
    """, (store_id, dates[0], dates[-1]))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return jsonify({"error": "No data for that week"}), 404

    df = pd.DataFrame(rows, columns=["product_name", "date", "produced", "waste"])

    # Pivot into AM/PM columns
    output = {}
    for product in df["product_name"].unique():
        product_rows = df[df["product_name"] == product]

        am_values = []
        pm_values = []

        for d in dates:
            row = product_rows[product_rows["date"] == d]
            if row.empty:
                am_values.append(0)
                pm_values.append(0)
            else:
                am_values.append(int(row["produced"].iloc[0]))
                pm_values.append(int(row["waste"].iloc[0]))

        output[product] = am_values + pm_values

    # Build final DataFrame
    columns = []
    for d in dates:
        columns.append(f"{d} AM")
        columns.append(f"{d} PM")

    final_df = pd.DataFrame.from_dict(output, orient="index", columns=columns)
    final_df.index.name = "Product"

    path = "/tmp/throwaway_export.xlsx"
    final_df.to_excel(path)

    return send_file(path, as_attachment=True)
