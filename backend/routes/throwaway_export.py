from flask import Blueprint, request, send_file, jsonify
import pandas as pd
from datetime import timedelta, datetime
from models.db import get_connection
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
import os

throwaway_export_bp = Blueprint("throwaway_export", __name__, url_prefix="/throwaway")

@throwaway_export_bp.get("/export")
def export_throwaway():
    """Export weekly data in AM/PM format matching the import template"""
    store_id = request.args.get("store_id", type=int)
    week_start = request.args.get("week_start")  # YYYY-MM-DD (Sunday)

    if not store_id:
        return jsonify({"error": "store_id required"}), 400
    
    # Default to current week's Sunday if not provided
    if not week_start:
        today = datetime.now().date()
        days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
        week_start = today - timedelta(days=days_since_sunday)
    else:
        week_start = pd.to_datetime(week_start).date()
    
    dates = [week_start + timedelta(days=i) for i in range(7)]

    conn = get_connection()
    cur = conn.cursor()

    # Fetch all active products
    cur.execute("""
        SELECT product_id, product_name, product_type
        FROM products
        WHERE is_active = TRUE
        ORDER BY product_type, product_name
    """)
    products = cur.fetchall()

    # Fetch production and waste data
    cur.execute("""
        SELECT 
            p.product_name,
            dp.production_date AS date,
            COALESCE(dp.quantity_produced, 0) AS produced,
            COALESCE(dt.quantity_thrown, 0) AS waste
        FROM products p
        LEFT JOIN daily_production dp ON p.product_id = dp.product_id
            AND dp.store_id = %s
            AND dp.production_date BETWEEN %s AND %s
        LEFT JOIN daily_throwaway dt ON p.product_id = dt.product_id
            AND dt.store_id = %s
            AND dt.throwaway_date BETWEEN %s AND %s
        WHERE p.is_active = TRUE
        ORDER BY p.product_type, p.product_name, dp.production_date
    """, (store_id, dates[0], dates[-1], store_id, dates[0], dates[-1]))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Build data structure: {product_name: [am_day1, pm_day1, am_day2, pm_day2, ...]}
    data = {}
    for product in products:
        product_name = product[1]
        data[product_name] = [0] * 14  # 7 days × 2 (AM/PM)

    # Fill in actual data
    for row in rows:
        product_name, date, produced, waste = row
        if product_name not in data:
            continue
        
        # Find the day index (0-6)
        if date:
            try:
                day_index = dates.index(date)
                data[product_name][day_index * 2] = int(produced)  # AM
                data[product_name][day_index * 2 + 1] = int(waste)  # PM
            except (ValueError, IndexError):
                continue

    # Create Excel with proper formatting
    rows_list = []
    
    # Header row 1: Week title
    header_row_1 = ["Product"] + [dates[0].strftime("%m/%d/%y")] + [""] * 13
    rows_list.append(header_row_1)
    
    # Header row 2: Base date
    header_row_2 = [""] + [dates[0].strftime("%B %d, %Y")] + [""] * 13
    rows_list.append(header_row_2)
    
    # Empty row
    rows_list.append([""] * 15)
    
    # Day header row
    day_headers = [""]
    for i, date in enumerate(dates):
        day_name = date.strftime("%A")
        day_headers.extend([day_name, ""])
    rows_list.append(day_headers)
    
    # AM/PM sub-header row
    am_pm_headers = ["Product"]
    for _ in range(7):
        am_pm_headers.extend(["AM", "PM"])
    rows_list.append(am_pm_headers)
    
    # Data rows
    for product_name, values in data.items():
        row = [product_name] + values
        rows_list.append(row)

    # Create DataFrame and export
    df = pd.DataFrame(rows_list)
    
    filename = f"dunkin_weekly_export_{week_start.strftime('%Y%m%d')}.xlsx"
    filepath = f"/tmp/{filename}"
    
    df.to_excel(filepath, index=False, header=False)
    
    # Apply formatting
    wb = load_workbook(filepath)
    ws = wb.active
    
    # Format header rows
    for col in range(1, 16):
        ws.cell(1, col).font = Font(bold=True, size=12)
        ws.cell(4, col).font = Font(bold=True)
        ws.cell(5, col).font = Font(bold=True)
        ws.cell(5, col).alignment = Alignment(horizontal='center')
    
    # Format product column
    for row in range(6, len(rows_list) + 1):
        ws.cell(row, 1).font = Font(bold=True)
    
    # Set column widths
    ws.column_dimensions['A'].width = 25
    for col in range(2, 16):
        ws.column_dimensions[chr(64 + col)].width = 10
    
    wb.save(filepath)

    return send_file(filepath, as_attachment=True, download_name=filename)

