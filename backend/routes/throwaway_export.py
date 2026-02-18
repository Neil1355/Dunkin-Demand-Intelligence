from flask import Blueprint, request, send_file, jsonify
import pandas as pd
from datetime import timedelta, datetime
from models.db import get_connection, return_connection
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
import os

throwaway_export_bp = Blueprint("throwaway_export", __name__, url_prefix="/throwaway")

@throwaway_export_bp.get("/export")
def export_throwaway():
    """Export weekly data in AM/PM format matching the import template"""
    try:
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
        try:
            cur = conn.cursor()

            # Fetch all active products
            cur.execute("""
                SELECT product_id, product_name, product_type
                FROM products
                WHERE is_active = TRUE
                ORDER BY product_type, product_name
            """)
            products = cur.fetchall()
            
            if not products:
                cur.close()
                return jsonify({"error": "No products found. Please add products first."}), 404

            # Fetch production and waste data
            cur.execute("""
                SELECT 
                    p.product_name,
                    dp.date,
                    COALESCE(dp.quantity, 0) AS produced,
                    COALESCE(dt.waste, 0) AS waste
                FROM products p
                LEFT JOIN daily_production dp ON p.product_id = dp.product_id
                    AND dp.store_id = %s
                    AND dp.date BETWEEN %s AND %s
                LEFT JOIN daily_throwaway dt ON p.product_id = dt.product_id
                    AND dt.store_id = %s
                    AND dt.date BETWEEN %s AND %s
                    AND dp.date = dt.date
                WHERE p.is_active = TRUE
                ORDER BY p.product_type, p.product_name, dp.date
            """, (store_id, dates[0], dates[-1], store_id, dates[0], dates[-1]))

            rows = cur.fetchall()
            cur.close()

            # Build data structure: {product_name: [am_day1, pm_day1, am_day2, pm_day2, ...]}
            data = {}
            for product in products:
                product_name = product['product_name']
                data[product_name] = [0] * 14  # 7 days × 2 (AM/PM)

            # Fill in actual data
            for row in rows:
                product_name = row['product_name']
                date = row['date']
                produced = row['produced']
                waste = row['waste']
                
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

            # Group products by type
            product_groups = {
                'croissant': [],
                'bagel': [],
                'donut': [],
                'muffin': [],
                'bakery': [],
                'munchkin': [],
                'other': []
            }
            
            for product in products:
                product_type = product['product_type']
                product_name = product['product_name']
                if product_type in product_groups:
                    product_groups[product_type].append(product_name)
                else:
                    product_groups['other'].append(product_name)

            # Create Excel with proper formatting matching template
            rows_list = []
            
            # Row 0: Store info
            store_row = [f"Store PC# : {store_id}"] + [""] * 14
            rows_list.append(store_row)
            
            # Row 1: Dates
            date_row = ["DATE:"] + [dates[i // 2].strftime("%m/%d/%y") if i % 2 == 0 else "" for i in range(14)]
            rows_list.append(date_row)
            
            # Row 2: Day names
            day_row = [""]
            for date in dates:
                day_name = date.strftime("%a").upper()
                day_row.extend([day_name, ""])
            rows_list.append(day_row)
            
            # Row 3: AM/PM headers
            am_pm_headers = [""]
            for _ in range(7):
                am_pm_headers.extend(["AM", "PM"])
            rows_list.append(am_pm_headers)

            # Add products by category with section headers
            category_order = [
                ('croissant', 'Plain Croissants'),
                ('bagel', 'Bagels'),
                ('donut', 'Donuts'),
                ('muffin', 'Muffins'),
                ('bakery', 'Fancies'),
                ('munchkin', 'Munchkins'),
                ('other', 'Other Items')
            ]
            
            total_produced = [0] * 7
            total_waste = [0] * 7
            
            for product_type, category_name in category_order:
                items = product_groups.get(product_type, [])
                if not items:
                    continue
                
                # Add category header row (bold, will be formatted later)
                category_row = [category_name] + [""] * 14
                rows_list.append(category_row)
                
                # Add products in this category
                for product_name in items:
                    values = data.get(product_name, [0] * 14)
                    row = [product_name] + values
                    rows_list.append(row)
                    
                    # Accumulate totals
                    for day in range(7):
                        total_produced[day] += values[day * 2]
                        total_waste[day] += values[day * 2 + 1]
                
                # Add empty row after each category
                rows_list.append([""] * 15)
            
            # Add totals section
            rows_list.append([""] * 15)  # Empty row
            
            # Donuts Bought (total produced)
            bought_row = ["Donuts Bought"]
            for val in total_produced:
                bought_row.extend([val if val > 0 else "", ""])
            rows_list.append(bought_row)
            
            # Calculate Donuts Sold
            sold_row = ["Donuts Sold"]
            for day in range(7):
                sold = total_produced[day] - total_waste[day]
                sold_row.extend([sold if sold > 0 else "", ""])
            rows_list.append(sold_row)
            
            # Difference
            diff_row = ["Difference"]
            for val in total_waste:
                diff_row.extend([val if val > 0 else "", ""])
            rows_list.append(diff_row)
            
            # Throwaway (waste in PM columns)
            throw_row = ["Throwaway"]
            for val in total_waste:
                throw_row.extend(["", val if val > 0 else ""])
            rows_list.append(throw_row)

            # Create DataFrame and export
            df = pd.DataFrame(rows_list)
            
            filename = f"dunkin_weekly_export_{week_start.strftime('%Y%m%d')}.xlsx"
            filepath = f"/tmp/{filename}"
            
            try:
                df.to_excel(filepath, index=False, header=False)
                
                # Apply formatting to match template
                wb = load_workbook(filepath)
                ws = wb.active
                
                # Blue fill for category headers
                blue_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                light_blue_fill = PatternFill(start_color="B4C7E7", end_color="B4C7E7", fill_type="solid")
                
                # Format row 1 (Store info) - bold
                ws.cell(1, 1).font = Font(bold=True, size=11)
                
                # Format row 2 (Dates) - bold
                for col in range(1, 16):
                    cell = ws.cell(2, col)
                    if cell.value:
                        cell.font = Font(bold=True, size=10)
                
                # Format row 3 (Day names) - bold, centered
                for col in range(1, 16):
                    cell = ws.cell(3, col)
                    if cell.value:
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(horizontal='center')
                
                # Format row 4 (AM/PM) - bold, centered
                for col in range(1, 16):
                    cell = ws.cell(4, col)
                    if cell.value:
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(horizontal='center')
                
                # Track category header rows for blue formatting
                category_header_rows = []
                
                # Format data rows starting from row 5
                for row_idx in range(5, len(rows_list) + 1):
                    cell_a = ws.cell(row_idx, 1)
                    cell_value = str(cell_a.value).strip() if cell_a.value else ""
                    
                    # Check if this is a category header
                    is_category = False
                    category_names = ['Plain Croissants', 'Bagels', 'Donuts', 'Muffins', 'Fancies', 'Munchkins', 'Other Items']
                    if cell_value in category_names:
                        is_category = True
                        category_header_rows.append(row_idx)
                    
                    # Check if this is a totals row
                    is_total = cell_value in ['Donuts Bought', 'Donuts Sold', 'Difference', 'Throwaway']
                    
                    if is_category:
                        # Category header: Blue background, bold, white text
                        for col in range(1, 16):
                            cell = ws.cell(row_idx, col)
                            cell.fill = blue_fill
                            cell.font = Font(bold=True, color="FFFFFF", size=11)
                    elif is_total:
                        # Totals row: bold
                        cell_a.font = Font(bold=True)
                    else:
                        # Regular product row: bold first column only
                        if cell_value:
                            cell_a.font = Font(bold=False)
                
                # Set column widths
                ws.column_dimensions['A'].width = 30
                for col_letter in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']:
                    ws.column_dimensions[col_letter].width = 8
                
                # Center align all data columns (B-O)
                for row_idx in range(1, len(rows_list) + 1):
                    for col in range(2, 16):
                        cell = ws.cell(row_idx, col)
                        if cell.value is not None and cell.value != "":
                            cell.alignment = Alignment(horizontal='center',vertical='center')
                
                wb.save(filepath)

                return send_file(filepath, as_attachment=True, download_name=filename)
                
            except Exception as file_error:
                print(f"Excel generation error: {file_error}")
                return jsonify({"error": f"Failed to generate Excel file: {str(file_error)}"}), 500
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

