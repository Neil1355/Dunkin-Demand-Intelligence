import os
import sys
import argparse
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. FIX PYTHON PATH SO "backend" CAN BE IMPORTED
# ---------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))          # backend/scripts
BACKEND_DIR = os.path.dirname(CURRENT_DIR)                        # backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)                       # project root
sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------
# 2. LOAD .env EXPLICITLY FROM PROJECT ROOT
# ---------------------------------------------------------
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_PATH)
print("DEBUG USING:", os.getenv("DATABASE_URL"))

# ---------------------------------------------------------
# 3. IMPORT DB CONNECTION (NOW THAT .env IS LOADED)
# ---------------------------------------------------------
from backend.models.db import get_connection

# ---------------------------------------------------------
# 4. LOAD PRODUCT MAP FROM DATABASE
# ---------------------------------------------------------
def load_product_map(cur):
    """Load all products from DB and return name → id mapping."""
    cur.execute("SELECT product_id, product_name FROM public.products WHERE is_active = TRUE")
    rows = cur.fetchall()
    return {name.strip(): pid for pid, name in rows}

# ---------------------------------------------------------
# 5. ARGUMENT PARSER
# ---------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="Import weekly throwaway sheet")
    parser.add_argument("--store", type=int, required=True, help="Store ID")
    parser.add_argument("--file", type=str, required=True, help="Path to Excel file")
    return parser.parse_args()

# ---------------------------------------------------------
# 6. MAIN IMPORT LOGIC
# ---------------------------------------------------------
def main():
    args = parse_arguments()
    STORE_ID = args.store
    EXCEL_PATH = args.file

    print(f"📄 Loading Excel: {EXCEL_PATH}")
    print(f"🏪 Store ID: {STORE_ID}")

    # Load raw sheet
    df = pd.read_excel(EXCEL_PATH, header=None)

    # Extract base date (row 1, col 1)
    base_date_raw = df.iloc[1, 1]
    base_date = pd.to_datetime(base_date_raw).date()
    print("📅 Base date (Sunday):", base_date)

    # Generate 7 dates (Sun → Sat)
    dates = [base_date + timedelta(days=i) for i in range(7)]

    # Product rows start at row 4
    start_row = 4

    # AM/PM columns: 14 columns starting at col 1
    waste_cols = list(range(1, 15))

    # Connect to DB
    conn = get_connection()
    cur = conn.cursor()
    print("DEBUG DATABASE_URL FROM ENV:", os.getenv("DATABASE_URL"))

    cur.execute("SELECT current_database(), current_user;")
    print("DEBUG ACTUAL DB:", cur.fetchone())

    # Load dynamic product map
    PRODUCT_MAP = load_product_map(cur)
    print(f"🔄 Loaded {len(PRODUCT_MAP)} products from DB")

    # Rows to skip (totals, summaries)
    SKIP_ROWS = {
        "Donuts Bought",
        "Donuts Sold",
        "Difference",
        "Throwaway",
        "Tot PM Donut Throw"
    }

    # Loop through product rows
    for row in range(start_row, len(df)):
        product_name = df.iloc[row, 0]

        if pd.isna(product_name):
            continue

        product_name = str(product_name).strip()

        # Skip summary rows
        if product_name in SKIP_ROWS:
            continue

        # Skip unknown products
        if product_name not in PRODUCT_MAP:
            print(f"⚠️ Unknown product in Excel: {product_name}")
            continue

        product_id = PRODUCT_MAP[product_name]

        # Extract 14 waste values
        values = df.iloc[row, waste_cols].fillna(0).tolist()

        # Insert AM/PM for each day
        for day_index in range(7):
            am = int(values[day_index * 2])
            pm = int(values[day_index * 2 + 1])
            date = dates[day_index]

            # Insert AM
            cur.execute("""
                INSERT INTO public.daily_throwaway
                (store_id, product_id, throwaway_date, quantity_thrown)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, throwaway_date)
                DO UPDATE SET quantity_thrown = EXCLUDED.quantity_thrown;
            """, (STORE_ID, product_id, date, am))

            # Insert PM
            cur.execute("""
                INSERT INTO public.daily_throwaway
                (store_id, product_id, throwaway_date, quantity_thrown)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, throwaway_date)
                DO UPDATE SET quantity_thrown = EXCLUDED.quantity_thrown;
            """, (STORE_ID, product_id, date, pm))

        print(f"✅ Imported: {product_name}")

    conn.commit()
    cur.close()
    conn.close()

    print("\n🎉 Weekly throwaway import complete!")

# ---------------------------------------------------------
# 7. ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()