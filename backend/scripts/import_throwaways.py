import os
import sys
import argparse
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

# Load .env
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path=ENV_PATH)

print("DEBUG USING:", os.getenv("DATABASE_URL"))
print("DEBUG ENV PATH:", ENV_PATH)
print("ENV FILE EXISTS:", os.path.exists(ENV_PATH))

from backend.models.db import get_connection


# ---------------------------------------------------------
# Load product map
# ---------------------------------------------------------
def load_product_map(cur):
    cur.execute("""
        SELECT product_id, product_name 
        FROM public.products 
        WHERE is_active = TRUE
    """)
    rows = cur.fetchall()

    product_map = {}
    for row in rows:
        if isinstance(row, dict):
            pid = row["product_id"]
            name = row["product_name"]
        else:
            pid, name = row

        product_map[name.strip().lower()] = pid

    return product_map


# ---------------------------------------------------------
# CLI args
# ---------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="Import weekly throwaway sheet")
    parser.add_argument("--store", type=int, required=True)
    parser.add_argument("--file", type=str, required=True)
    return parser.parse_args()


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------
def safe_int(x):
    try:
        if pd.isna(x):
            return 0
        x = str(x).strip()
        if x == "":
            return 0
        return int(float(x))
    except:
        return 0


# ---------------------------------------------------------
# Main importer
# ---------------------------------------------------------
def main():
    args = parse_arguments()
    STORE_ID = args.store
    EXCEL_PATH = args.file

    print(f"\n[LOAD] Loading Excel: {EXCEL_PATH}")
    print(f"[STORE] Store ID: {STORE_ID}")

    df = pd.read_excel(EXCEL_PATH, header=None)

    # Base date (Sunday)
    base_date_raw = df.iloc[1, 1]
    base_date = pd.to_datetime(base_date_raw).date()
    print(f"[DATE] Base date (Sunday): {base_date}")

    # 7 days of the week
    dates = [base_date + timedelta(days=i) for i in range(7)]

    start_row = 4
    cols = list(range(1, 15))  # 14 columns: AM/PM pairs for 7 days

    conn = get_connection()
    cur = conn.cursor()

    # Debug info
    cur.execute("SELECT current_database(), current_user;")
    print("[DEBUG] DB/USER:", cur.fetchone())

    cur.execute("SELECT COUNT(*) FROM public.products;")
    print("[DEBUG] Product count:", cur.fetchone())

    cur.execute("SELECT inet_server_addr(), inet_server_port();")
    print("[DEBUG] Server:", cur.fetchone())

    PRODUCT_MAP = load_product_map(cur)
    print(f"[LOAD] Loaded {len(PRODUCT_MAP)} products from public.products")

    if len(PRODUCT_MAP) == 0:
        print("[ERROR] No products loaded.")
        conn.close()
        return

    SKIP_ROWS = {
        "Donuts Bought",
        "Donuts Sold",
        "Difference",
        "Throwaway",
        "Tot PM Donut Throw"
    }

    imported_count = 0

    # ---------------------------------------------------------
    # Iterate through product rows
    # ---------------------------------------------------------
    for row in range(start_row, len(df)):
        product_name = df.iloc[row, 0]

        if pd.isna(product_name):
            continue

        product_name = str(product_name).strip()
        product_key = product_name.lower()

        if product_name in SKIP_ROWS:
            continue

        # Read AM/PM values FIRST (prevents index errors)
        values = df.iloc[row, cols].fillna(0).tolist()

        # Auto-add seasonal products AFTER reading row
        if product_key not in PRODUCT_MAP:
            print(f"[AUTO-ADD] New seasonal product detected: {product_name}")

            cur.execute("""
                INSERT INTO public.products (product_name, product_type, is_active)
                VALUES (%s, 'other', TRUE)
                RETURNING product_id;
            """, (product_name,))

            row_dict = cur.fetchone()
            new_id = row_dict["product_id"]
            PRODUCT_MAP[product_key] = new_id

        product_id = PRODUCT_MAP[product_key]

        # Extract produced (AM) and waste (PM)
        produced_list = []
        waste_list = []

        for i in range(0, 14, 2):
            am = safe_int(values[i])       # produced
            pm = safe_int(values[i + 1])   # waste

            produced_list.append(am)
            waste_list.append(pm)

        # Insert 7 days
        for day_index in range(7):
            date = dates[day_index]
            produced = produced_list[day_index]
            waste = waste_list[day_index]

            # Optional: skip rows where both are zero
            if produced == 0 and waste == 0:
                continue

            cur.execute("""
                INSERT INTO public.daily_throwaway
                (store_id, product_id, date, produced, waste)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (store_id, product_id, date)
                DO UPDATE SET 
                    produced = EXCLUDED.produced,
                    waste = EXCLUDED.waste;
            """, (STORE_ID, product_id, date, produced, waste))

        print(f"[OK] Imported: {product_name}")
        imported_count += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n[DONE] Import complete: {imported_count} products, {imported_count * 7} daily entries processed.")


if __name__ == "__main__":
    main()