"""
Dashboard Routes
Provides endpoints for displaying imported data and analytics to the frontend
"""

from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection
from utils.jwt_handler import require_auth
from datetime import datetime, timedelta

bp = Blueprint("dashboard_data", __name__, url_prefix="/api/v1/dashboard")


# =========================================================
# HANDLE OPTIONS PREFLIGHT REQUESTS (CORS)
# =========================================================

@bp.route('/imports', methods=['OPTIONS'])
@bp.route('/production-summary', methods=['OPTIONS'])
@bp.route('/waste-summary', methods=['OPTIONS'])
@bp.route('/quick-stats', methods=['OPTIONS'])
def handle_preflight():
    """Handle CORS preflight requests - must NOT require authentication"""
    return '', 204


# =========================================================
# IMPORT STATUS & HISTORY
# =========================================================

@bp.get("/imports")
@require_auth
def get_recent_imports():
    """
    Get recently imported data grouped by type and date
    Shows import status and record counts
    
    Query params:
    - store_id: int (required)
    - days: int (default=30)
    - import_type: str (optional - 'throwaway', 'production', etc)
    """
    try:
        store_id = request.args.get("store_id", type=int)
        days_back = request.args.get("days", type=int, default=30)
        import_type = request.args.get("import_type", type=str, default=None)
        
        if not store_id:
            return jsonify({"error": "store_id required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Get throwaway imports
        cur.execute("""
            SELECT
                DATE(dt.created_at) AS import_date,
                COUNT(DISTINCT dt.product_id) AS products_imported,
                COUNT(*) AS total_records,
                SUM(dt.produced) AS total_produced,
                SUM(dt.waste) AS total_waste,
                'throwaway' AS import_type
            FROM public.daily_throwaway dt
            WHERE dt.store_id = %s
              AND dt.created_at >= NOW() - INTERVAL '%s days'
              AND dt.source = 'excel'
            GROUP BY DATE(dt.created_at)
            ORDER BY import_date DESC
        """, (store_id, days_back))
        
        throwaway_imports = [dict(row) for row in cur.fetchall()]
        
        # Get production imports
        cur.execute("""
            SELECT
                DATE(dp.created_at) AS import_date,
                COUNT(DISTINCT dp.product_id) AS products_imported,
                COUNT(*) AS total_records,
                SUM(dp.quantity) AS total_quantity,
                'production' AS import_type
            FROM public.daily_production dp
            WHERE dp.store_id = %s
              AND dp.created_at >= NOW() - INTERVAL '%s days'
              AND dp.source = 'excel'
            GROUP BY DATE(dp.created_at)
            ORDER BY import_date DESC
        """, (store_id, days_back))
        
        production_imports = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        return_connection(conn)
        
        # Combine results
        all_imports = throwaway_imports + production_imports
        all_imports.sort(key=lambda x: x['import_date'], reverse=True)
        
        return jsonify({
            "status": "success",
            "imports": all_imports,
            "summary": {
                "total_import_dates": len(set(imp['import_date'] for imp in all_imports)),
                "throwaway_imports": len(throwaway_imports),
                "production_imports": len(production_imports)
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] get_recent_imports: {e}")
        return jsonify({"error": str(e)}), 500


# =========================================================
# PRODUCTION SUMMARY
# =========================================================

@bp.get("/production-summary")
@require_auth
def get_production_summary():
    """
    Get production metrics and trends
    
    Query params:
    - store_id: int (required)
    - days: int (default=7)
    - product_id: int (optional - filter by product)
    - product_type: str (optional - donut|munchkin|...)
    """
    try:
        store_id = request.args.get("store_id", type=int)
        days_back = request.args.get("days", type=int, default=7)
        product_id = request.args.get("product_id", type=int, default=None)
        product_type = request.args.get("product_type", type=str, default=None)
        
        if not store_id:
            return jsonify({"error": "store_id required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
                # Daily production trend (use imported throwaway produced values)
        if product_id:
            cur.execute("""
                SELECT
                            dt.date,
                            dt.produced AS quantity,
                            dt.waste,
                    p.product_name
                                FROM public.daily_throwaway dt
                                JOIN public.products p ON p.product_id = dt.product_id
                                WHERE dt.store_id = %s
                                    AND dt.product_id = %s
                                    AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
                                ORDER BY dt.date DESC
            """, (store_id, product_id, days_back))
        elif product_type:
            cur.execute("""
                SELECT
                    dt.date,
                    SUM(dt.produced) AS total_quantity,
                    SUM(dt.waste) AS total_waste,
                    COUNT(DISTINCT dt.product_id) AS products_produced
                FROM public.daily_throwaway dt
                JOIN public.products p ON p.product_id = dt.product_id
                WHERE dt.store_id = %s
                  AND LOWER(p.product_type) = LOWER(%s)
                  AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY dt.date
                ORDER BY dt.date DESC
            """, (store_id, product_type, days_back))
        else:
            cur.execute("""
                SELECT
                                        dt.date,
                                        SUM(dt.produced) AS total_quantity,
                    SUM(dt.waste) AS total_waste,
                                        COUNT(DISTINCT dt.product_id) AS products_produced
                                FROM public.daily_throwaway dt
                                WHERE dt.store_id = %s
                                    AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
                                GROUP BY dt.date
                                ORDER BY dt.date DESC
            """, (store_id, days_back))
        
        daily_data = [dict(row) for row in cur.fetchall()]
        
        # Summary stats
        if product_type:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT dt.date) AS days_with_data,
                    COUNT(DISTINCT dt.product_id) AS unique_products,
                    SUM(dt.produced) AS total_produced,
                    SUM(dt.waste) AS total_waste,
                    AVG(dt.produced) AS avg_daily_production,
                    MAX(dt.produced) AS peak_production
                FROM public.daily_throwaway dt
                JOIN public.products p ON p.product_id = dt.product_id
                WHERE dt.store_id = %s
                  AND LOWER(p.product_type) = LOWER(%s)
                  AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
            """, (store_id, product_type, days_back))
        else:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT dt.date) AS days_with_data,
                    COUNT(DISTINCT dt.product_id) AS unique_products,
                    SUM(dt.produced) AS total_produced,
                    SUM(dt.waste) AS total_waste,
                    AVG(dt.produced) AS avg_daily_production,
                    MAX(dt.produced) AS peak_production
                FROM public.daily_throwaway dt
                WHERE dt.store_id = %s
                  AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
            """, (store_id, days_back))
        
        summary = dict(cur.fetchone())
        
        cur.close()
        return_connection(conn)
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "daily_data": daily_data
        }), 200
        
    except Exception as e:
        print(f"[ERROR] get_production_summary: {e}")
        return jsonify({"error": str(e)}), 500


# =========================================================
# WASTE SUMMARY
# =========================================================

@bp.get("/waste-summary")
@require_auth
def get_waste_summary():
    """
    Get waste/throwaway metrics and trends
    
    Query params:
    - store_id: int (required)
    - days: int (default=7)
    - product_id: int (optional - filter by product)
    """
    try:
        store_id = request.args.get("store_id", type=int)
        days_back = request.args.get("days", type=int, default=7)
        product_id = request.args.get("product_id", type=int, default=None)
        
        if not store_id:
            return jsonify({"error": "store_id required"}), 400
        
        print(f"[WASTE-SUMMARY DEBUG] Fetching waste for store_id={store_id}, days={days_back}")
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Daily waste trend
        if product_id:
            cur.execute("""
                SELECT
                    dt.date,
                    dt.produced,
                    dt.waste,
                    CASE 
                        WHEN dt.produced > 0 THEN ROUND(100.0 * dt.waste / dt.produced, 2)
                        ELSE 0
                    END AS waste_percentage,
                    p.product_name
                FROM public.daily_throwaway dt
                JOIN public.products p ON p.product_id = dt.product_id
                WHERE dt.store_id = %s
                  AND dt.product_id = %s
                  AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY dt.date DESC
            """, (store_id, product_id, days_back))
        else:
            cur.execute("""
                SELECT
                    dt.date,
                    SUM(dt.produced) AS total_produced,
                    SUM(dt.waste) AS total_waste,
                    CASE 
                        WHEN SUM(dt.produced) > 0 THEN ROUND(100.0 * SUM(dt.waste) / SUM(dt.produced), 2)
                        ELSE 0
                    END AS waste_percentage,
                    COUNT(DISTINCT dt.product_id) AS products
                FROM public.daily_throwaway dt
                WHERE dt.store_id = %s
                  AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY dt.date
                ORDER BY dt.date DESC
            """, (store_id, days_back))
        
        daily_data = [dict(row) for row in cur.fetchall()]
        print(f"[WASTE-SUMMARY DEBUG] Found {len(daily_data)} daily records")
        if daily_data:
            print(f"[WASTE-SUMMARY DEBUG] Sample record: {daily_data[0]}")
        
        # Summary stats
        cur.execute("""
            SELECT
                COUNT(DISTINCT dt.date) AS days_with_data,
                COUNT(DISTINCT dt.product_id) AS unique_products,
                SUM(dt.produced) AS total_produced,
                SUM(dt.waste) AS total_waste,
                CASE 
                    WHEN SUM(dt.produced) > 0 THEN ROUND(100.0 * SUM(dt.waste) / SUM(dt.produced), 2)
                    ELSE 0
                END AS overall_waste_percentage,
                AVG(dt.waste) AS avg_daily_waste,
                MAX(dt.waste) AS peak_waste
            FROM public.daily_throwaway dt
            WHERE dt.store_id = %s
              AND dt.date >= CURRENT_DATE - INTERVAL '%s days'
        """, (store_id, days_back))
        
        summary = dict(cur.fetchone())
        
        cur.close()
        return_connection(conn)
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "daily_data": daily_data
        }), 200
        
    except Exception as e:
        print(f"[ERROR] get_waste_summary: {e}")
        return jsonify({"error": str(e)}), 500


# =========================================================
# QUICK STATS
# =========================================================

@bp.get("/quick-stats")
@require_auth
def get_quick_stats():
    """
    Get high-level KPIs for dashboard cards
    
    Query params:
    - store_id: int (required)
    """
    try:
        store_id = request.args.get("store_id", type=int)
        
        if not store_id:
            return jsonify({"error": "store_id required"}), 400
        
        try:
            conn = get_connection()
        except Exception as e:
            print(f"[ERROR] get_quick_stats: Database connection failed: {e}")
            return jsonify({"error": f"Database connection failed: {str(e)}"}), 500
        
        if not conn:
            return jsonify({"error": "Could not get database connection"}), 500
            
        try:
            cur = conn.cursor()
            
            # Last 7 days stats
            cur.execute("""
                SELECT
                    SUM(dt.produced) AS total_produced_7d,
                    SUM(dt.waste) AS total_waste_7d,
                    COUNT(DISTINCT dt.date) AS days_recorded_7d,
                    COUNT(DISTINCT dt.product_id) AS unique_products_7d
                FROM public.daily_throwaway dt
                WHERE dt.store_id = %s
                  AND dt.date >= CURRENT_DATE - INTERVAL '7 days'
            """, (store_id,))
            
            result = cur.fetchone()
            
            # Handle case where no data exists
            if result is None:
                stats_7d = {
                    "total_produced": 0,
                    "total_waste": 0,
                    "days_recorded": 0,
                    "unique_products": 0,
                    "waste_ratio": 0
                }
            else:
                # Handle RealDictCursor or tuple results
                if isinstance(result, dict):
                    stats_7d = {
                        "total_produced": result.get("total_produced_7d") or 0,
                        "total_waste": result.get("total_waste_7d") or 0,
                        "days_recorded": result.get("days_recorded_7d") or 0,
                        "unique_products": result.get("unique_products_7d") or 0
                    }
                else:
                    stats_7d = {
                        "total_produced": result[0] or 0,
                        "total_waste": result[1] or 0,
                        "days_recorded": result[2] or 0,
                        "unique_products": result[3] or 0
                    }
                
                # Calculate waste ratio
                if stats_7d["total_produced"] > 0:
                    stats_7d["waste_ratio"] = round(100.0 * stats_7d["total_waste"] / stats_7d["total_produced"], 2)
                else:
                    stats_7d["waste_ratio"] = 0
            
            # Most wasted product
            cur.execute("""
                SELECT
                    p.product_name,
                    SUM(dt.waste) AS total_waste
                FROM public.daily_throwaway dt
                JOIN public.products p ON p.product_id = dt.product_id
                WHERE dt.store_id = %s
                  AND dt.date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY p.product_id, p.product_name
                ORDER BY total_waste DESC
                LIMIT 3
            """, (store_id,))
            
            top_waste_rows = cur.fetchall()
            
            # Handle both RealDictCursor and tuple results
            if top_waste_rows and isinstance(top_waste_rows[0], dict):
                top_waste_products = [{"product": row["product_name"], "waste": row["total_waste"]} for row in top_waste_rows]
            else:
                top_waste_products = [{"product": row[0], "waste": row[1]} for row in top_waste_rows] if top_waste_rows else []
            
            cur.close()
            return_connection(conn)
            
            return jsonify({
                "status": "success",
                "stats_7d": stats_7d,
                "top_waste_products": top_waste_products
            }), 200
            
        except Exception as db_error:
            print(f"[ERROR] get_quick_stats: Database query failed: {db_error}")
            cur.close()
            return_connection(conn)
            return jsonify({"error": f"Database query failed: {str(db_error)}"}), 500
        
    except Exception as e:
        print(f"[ERROR] get_quick_stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
