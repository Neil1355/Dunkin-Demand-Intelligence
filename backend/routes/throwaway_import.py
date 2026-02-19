from flask import Blueprint, request, jsonify
import pandas as pd
from datetime import timedelta
from models.db import get_connection, return_connection
from utils.jwt_handler import require_auth

throwaway_import_bp = Blueprint("throwaway_import", __name__)


def safe_int(x):
    """Convert value to int, return 0 if invalid"""
    try:
        if pd.isna(x):
            return 0
        x = str(x).strip()
        if x == "":
            return 0
        return int(float(x))
    except:
        return 0


@throwaway_import_bp.post("/upload_throwaways")
@require_auth
def upload_throwaways():
    """
    Upload weekly throwaway sheet in AM/PM format
    Expected format:
    - Row 2, Column B: Base date (Sunday)
    - Row 4+: Product names in Column A, AM/PM data in columns B-O (14 columns for 7 days)
    - AM columns (even indexes): produced
    - PM columns (odd indexes): waste
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        store_id = request.form.get("store_id", type=int)

        if not store_id:
            return jsonify({"error": "store_id is required"}), 400

        # Read Excel without headers
        df = pd.read_excel(file, header=None)

        # Extract base date from Row 2, Column B (index [1, 1])
        base_date_raw = df.iloc[1, 1]
        base_date = pd.to_datetime(base_date_raw).date()  # type: ignore

        # Calculate 7 days starting from Sunday
        dates = [base_date + timedelta(days=i) for i in range(7)]

        # Data starts at row 4 (index 4)
        start_row = 4
        # Columns B-O (indexes 1-14): 14 columns for AM/PM pairs
        cols = list(range(1, 15))

        conn = get_connection()
        cur = conn.cursor()

        # Load existing products
        cur.execute("""
            SELECT product_id, product_name 
            FROM products 
            WHERE is_active = TRUE
        """)
        rows = cur.fetchall()

        product_map = {}
        for row in rows:
            product_map[row['product_name'].strip().lower()] = row['product_id']

        # Skip these row labels
        SKIP_ROWS = {
            "Donuts Bought",
            "Donuts Sold",
            "Difference",
            "Throwaway",
            "Tot PM Donut Throw"
        }

        imported_count = 0

        # Process each product row
        for row_idx in range(start_row, len(df)):
            product_name = df.iloc[row_idx, 0]

            if pd.isna(product_name):
                continue

            product_name = str(product_name).strip()
            product_key = product_name.lower()

            if product_name in SKIP_ROWS:
                continue

            # Read AM/PM values
            values = df.iloc[row_idx, cols].fillna(0).tolist()

            # Auto-add new products (seasonal items)
            if product_key not in product_map:
                print(f"[AUTO-ADD] New product detected: {product_name}")

                cur.execute("""
                    INSERT INTO products (product_name, product_type, is_active)
                    VALUES (%s, 'other', TRUE)
                    RETURNING product_id;
                """, (product_name,))

                result = cur.fetchone()
                new_id = result['product_id']
                product_map[product_key] = new_id

            product_id = product_map[product_key]

            # Extract produced (AM) and waste (PM) for each day
            for day_index in range(7):
                date = dates[day_index]
                
                # AM/PM pairs: columns are [AM_Sun, PM_Sun, AM_Mon, PM_Mon, ...]
                am_index = day_index * 2
                pm_index = day_index * 2 + 1
                
                produced = safe_int(values[am_index])
                waste = safe_int(values[pm_index])

                # Skip if both are zero
                if produced == 0 and waste == 0:
                    continue

                # Insert into daily_throwaway table
                cur.execute("""
                    INSERT INTO daily_throwaway
                    (store_id, product_id, date, produced, waste)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (store_id, product_id, date)
                    DO UPDATE SET 
                        produced = EXCLUDED.produced,
                        waste = EXCLUDED.waste;
                """, (store_id, product_id, date, produced, waste))

            imported_count += 1

        conn.commit()
        cur.close()
        return_connection(conn)

        return jsonify({
            "status": "success",
            "message": f"Successfully imported {imported_count} products",
            "imported": imported_count,
            "week_start": str(base_date),
            "week_end": str(dates[-1])
        }), 200

    except Exception as e:
        print(f"Error importing throwaways: {e}")
        return jsonify({"error": str(e)}), 500
