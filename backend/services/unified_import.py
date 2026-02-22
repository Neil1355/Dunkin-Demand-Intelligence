"""
Unified Import Service
Consolidates all xlsx/excel import logic for:
- Daily Throwaway (AM/PM format, 7-day week)
- Daily Production 
- Generic daily data

Provides consistent interface for all import types.
"""

import pandas as pd
from datetime import timedelta, datetime
from models.db import get_connection, return_connection
from typing import Dict, List, Tuple, Optional


class UnifiedImporter:
    """Main importer class handling all xlsx formats"""
    
    def __init__(self):
        self.import_history = []
    
    # =========================================================
    # HELPER FUNCTIONS
    # =========================================================
    
    @staticmethod
    def safe_int(x):
        """Convert value to int safely, return 0 if invalid"""
        try:
            if pd.isna(x):
                return 0
            x = str(x).strip()
            if x == "":
                return 0
            return int(float(x))
        except:
            return 0
    
    @staticmethod
    def load_product_map(conn) -> Dict[str, int]:
        """Load all active products into a map: {name_lower -> product_id}"""
        cur = conn.cursor()
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
    
    @staticmethod
    def auto_add_product(conn, product_name: str) -> int:
        """Auto-add a new product (seasonal) to the database"""
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO public.products (product_name, product_type, is_active)
            VALUES (%s, 'other', TRUE)
            RETURNING product_id;
        """, (product_name,))
        
        result = cur.fetchone()
        new_id = result["product_id"]
        conn.commit()
        
        return new_id
    
    # =========================================================
    # THROWAWAY IMPORTER (AM/PM Format, 7-day week)
    # =========================================================
    
    def import_weekly_throwaways(
        self, 
        excel_path: str, 
        store_id: int
    ) -> Dict:
        """
        Import weekly throwaway sheet in AM/PM format.
        
        Expected format:
        - Row 2, Column B: Base date (Sunday)
        - Row 4+: Product names in Column A, AM/PM data in columns B-O (14 columns = 7 days × 2)
        - AM columns (even indexes): produced
        - PM columns (odd indexes): waste
        
        Returns:
            {
                "status": "success" | "error",
                "message": str,
                "imported_count": int,
                "week_start": str,
                "week_end": str
            }
        """
        try:
            print(f"[LOAD] Loading throwaway Excel: {excel_path}, Store: {store_id}")
            
            df = pd.read_excel(excel_path, header=None)
            
            # Extract base date from Row 2, Column B (index [1, 1])
            base_date_raw = df.iloc[1, 1]
            base_date = pd.to_datetime(base_date_raw).date()  # type: ignore
            
            # 7 days starting from Sunday
            dates = [base_date + timedelta(days=i) for i in range(7)]
            
            # Data starts at row 4 (index 4)
            start_row = 4
            # Columns B-O (indexes 1-14): 14 columns for AM/PM pairs
            cols = list(range(1, 15))
            
            conn = get_connection()
            product_map = self.load_product_map(conn)
            
            # Skip these row labels
            SKIP_ROWS = {
                "Donuts Bought",
                "Donuts Sold",
                "Difference",
                "Throwaway",
                "Tot PM Donut Throw"
            }
            
            imported_count = 0
            cur = conn.cursor()
            
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
                    print(f"[AUTO-ADD] New product: {product_name}")
                    new_id = self.auto_add_product(conn, product_name)
                    product_map[product_key] = new_id
                
                product_id = product_map[product_key]
                
                # Extract produced (AM) and waste (PM) for each day
                for day_index in range(7):
                    date = dates[day_index]
                    
                    # AM/PM pairs: [AM_Sun, PM_Sun, AM_Mon, PM_Mon, ...]
                    am_index = day_index * 2
                    pm_index = day_index * 2 + 1
                    
                    produced = self.safe_int(values[am_index])
                    waste = self.safe_int(values[pm_index])
                    
                    # Skip if both are zero
                    if produced == 0 and waste == 0:
                        continue
                    
                    # Insert into daily_throwaway table
                    cur.execute("""
                        INSERT INTO public.daily_throwaway
                        (store_id, product_id, date, produced, waste, source)
                        VALUES (%s, %s, %s, %s, %s, 'excel')
                        ON CONFLICT (store_id, product_id, date)
                        DO UPDATE SET 
                            produced = EXCLUDED.produced,
                            waste = EXCLUDED.waste,
                            updated_at = NOW();
                    """, (store_id, product_id, date, produced, waste))
                
                imported_count += 1
            
            conn.commit()
            cur.close()
            return_connection(conn)
            
            result = {
                "status": "success",
                "message": f"Imported {imported_count} products",
                "imported_count": imported_count,
                "week_start": str(base_date),
                "week_end": str(dates[-1]),
                "import_type": "weekly_throwaways"
            }
            
            self.import_history.append(result)
            return result
            
        except Exception as e:
            print(f"[ERROR] Throwaway import failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "import_type": "weekly_throwaways"
            }
    
    # =========================================================
    # PRODUCTION IMPORTER (Generic format)
    # =========================================================
    
    def import_production_data(
        self,
        excel_path: str,
        store_id: int,
        date_column: str = "date",
        product_column: str = "product",
        quantity_column: str = "quantity"
    ) -> Dict:
        """
        Import production data from generic excel format.
        
        Expected columns: date, product_name, quantity_produced
        
        Returns:
            {
                "status": "success" | "error",
                "message": str,
                "imported_count": int
            }
        """
        try:
            print(f"[LOAD] Loading production Excel: {excel_path}, Store: {store_id}")
            
            df = pd.read_excel(excel_path)
            
            # Normalize column names to lowercase
            df.columns = [c.strip().lower() for c in df.columns]
            
            conn = get_connection()
            product_map = self.load_product_map(conn)
            
            imported_count = 0
            cur = conn.cursor()
            
            for idx, row in df.iterrows():
                try:
                    # Extract fields
                    date_val = pd.to_datetime(row[date_column]).date()  # type: ignore
                    product_name = str(row[product_column]).strip()
                    quantity = self.safe_int(row[quantity_column])
                    
                    if quantity == 0:
                        continue
                    
                    # Map product or auto-add
                    product_key = product_name.lower()
                    if product_key not in product_map:
                        print(f"[AUTO-ADD] New product: {product_name}")
                        new_id = self.auto_add_product(conn, product_name)
                        product_map[product_key] = new_id
                    
                    product_id = product_map[product_key]
                    
                    # Insert into daily_production
                    cur.execute("""
                        INSERT INTO public.daily_production
                        (store_id, product_id, date, quantity, source)
                        VALUES (%s, %s, %s, %s, 'excel')
                        ON CONFLICT (store_id, product_id, date)
                        DO UPDATE SET 
                            quantity = EXCLUDED.quantity,
                            updated_at = NOW();
                    """, (store_id, product_id, date_val, quantity))
                    
                    imported_count += 1
                    
                except Exception as row_error:
                    print(f"[WARN] Row {idx} skipped: {row_error}")
                    continue
            
            conn.commit()
            cur.close()
            return_connection(conn)
            
            result = {
                "status": "success",
                "message": f"Imported {imported_count} production records",
                "imported_count": imported_count,
                "import_type": "production_data"
            }
            
            self.import_history.append(result)
            return result
            
        except Exception as e:
            print(f"[ERROR] Production import failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "import_type": "production_data"
            }
    
    # =========================================================
    # GENERIC DATA IMPORTER
    # =========================================================
    
    def import_generic_data(
        self,
        excel_path: str,
        store_id: int,
        table_name: str,
        column_mapping: Dict[str, str]
    ) -> Dict:
        """
        Import generic daily data to any table.
        
        Args:
            excel_path: Path to xlsx file
            store_id: Store ID for the data
            table_name: Target table (e.g., 'daily_sales', 'daily_waste')
            column_mapping: {excel_col: table_col, ...}
        
        Returns:
            Result dictionary
        """
        try:
            print(f"[LOAD] Loading {table_name} data from {excel_path}")
            
            df = pd.read_excel(excel_path)
            df.columns = [c.strip().lower() for c in df.columns]
            
            conn = get_connection()
            product_map = self.load_product_map(conn)
            
            imported_count = 0
            cur = conn.cursor()
            
            for idx, row in df.iterrows():
                try:
                    # Build insert values
                    values = {"store_id": store_id}
                    
                    for excel_col, table_col in column_mapping.items():
                        if excel_col in row.index:
                            val = row[excel_col]
                            
                            # Special handling for product columns
                            if table_col == "product_id" and not isinstance(val, int):
                                product_key = str(val).strip().lower()
                                if product_key not in product_map:
                                    new_id = self.auto_add_product(conn, str(val).strip())
                                    product_map[product_key] = new_id
                                values[table_col] = product_map[product_key]
                            else:
                                values[table_col] = val
                    
                    # Build insert query
                    cols = ", ".join(values.keys())
                    placeholders = ", ".join(["%s"] * len(values))
                    
                    cur.execute(f"""
                        INSERT INTO public.{table_name} ({cols})
                        VALUES ({placeholders})
                    """, tuple(values.values()))
                    
                    imported_count += 1
                    
                except Exception as row_error:
                    print(f"[WARN] Row {idx} failed: {row_error}")
                    continue
            
            conn.commit()
            cur.close()
            return_connection(conn)
            
            result = {
                "status": "success",
                "message": f"Imported {imported_count} records to {table_name}",
                "imported_count": imported_count,
                "import_type": "generic",
                "table": table_name
            }
            
            self.import_history.append(result)
            return result
            
        except Exception as e:
            print(f"[ERROR] Generic import to {table_name} failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "import_type": "generic",
                "table": table_name
            }
    
    # =========================================================
    # HISTORY & TRACKING
    # =========================================================
    
    def get_import_history(self) -> List[Dict]:
        """Return all imports performed in this session"""
        return self.import_history
    
    def clear_history(self):
        """Clear import history"""
        self.import_history = []


# Singleton instance
_importer = UnifiedImporter()

def get_importer() -> UnifiedImporter:
    """Get the global importer instance"""
    return _importer
