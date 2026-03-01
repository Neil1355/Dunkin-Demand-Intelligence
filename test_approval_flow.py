#!/usr/bin/env python3
"""
Test script to verify approval flow and data visibility in dashboard
"""
import os
import sys
from datetime import date, timedelta

# Load environment variables from backend/.env
from dotenv import load_dotenv
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
load_dotenv(os.path.join(backend_dir, '.env'))

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.models.db import get_connection, return_connection

def test_approval_flow():
    """Test that approved submissions show up in dashboard queries"""
    
    conn = get_connection()
    cur = conn.cursor()
    
    print("=" * 70)
    print("DIAGNOSTIC: Testing Pending Waste Approval Flow")
    print("=" * 70)
    
    # Step 1: Check for recent pending submissions
    print("\n1️⃣  Checking pending waste submissions...")
    cur.execute("""
        SELECT 
            pws.id, pws.store_id, pws.submitter_name, pws.submission_date, 
            pws.status, COUNT(pwi.id) as item_count
        FROM pending_waste_submissions pws
        LEFT JOIN pending_waste_items pwi ON pwi.submission_id = pws.id
        WHERE pws.submission_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY pws.id
        ORDER BY pws.submitted_at DESC
        LIMIT 10
    """)
    
    submissions = cur.fetchall()
    if submissions:
        print(f"   Found {len(submissions)} recent submissions:")
        for sub in submissions:
            print(f"   - ID {sub['id']}: Store {sub['store_id']}, Status={sub['status']}, Items={sub['item_count']}, Date={sub['submission_date']}")
    else:
        print("   ❌ No recent submissions found")
        print("   → Create a test submission via QR code first")
    
    # Step 2: Check approved submissions and their items
    print("\n2️⃣  Checking approved/edited submissions with items...")
    cur.execute("""
        SELECT 
            pws.id, pws.store_id, pws.submission_date, pws.status,
            pwi.product_id, pwi.product_name, pwi.waste_quantity
        FROM pending_waste_submissions pws
        JOIN pending_waste_items pwi ON pwi.submission_id = pws.id
        WHERE pws.status IN ('approved', 'edited')
          AND pws.submission_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY pws.reviewed_at DESC
        LIMIT 20
    """)
    
    approved_items = cur.fetchall()
    if approved_items:
        print(f"   Found {len(approved_items)} approved items:")
        for item in approved_items[:5]:  # Show first 5
            print(f"   - Submission {item['id']}: {item['product_name']} (qty={item['waste_quantity']}, product_id={item['product_id']}, date={item['submission_date']})")
    else:
        print("   ⚠️  No approved items found in pending_waste_items")
        print("   → Approve a submission and try again")
    
    # Step 3: Check if data made it to daily_throwaway
    print("\n3️⃣  Checking daily_throwaway table (dashboard data source)...")
    cur.execute("""
        SELECT 
            dt.store_id, dt.product_id, p.product_name, dt.date, 
            dt.waste, dt.source, dt.created_at
        FROM daily_throwaway dt
        JOIN products p ON p.product_id = dt.product_id
        WHERE dt.date >= CURRENT_DATE - INTERVAL '7 days'
          AND dt.source = 'pending_approval'
        ORDER BY dt.created_at DESC
        LIMIT 20
    """)
    
    throwaway_records = cur.fetchall()
    if throwaway_records:
        print(f"   ✅ Found {len(throwaway_records)} records from pending approval:")
        for rec in throwaway_records[:5]:
            print(f"   - Store {rec['store_id']}: {rec['product_name']} (waste={rec['waste']}, date={rec['date']})")
    else:
        print("   ❌ No records found in daily_throwaway with source='pending_approval'")
        print("   → This means the INSERT is failing during approval")
    
    # Step 4: Check what dashboard endpoints would return
    print("\n4️⃣  Simulating dashboard waste-summary query...")
    cur.execute("""
        SELECT
            dt.date,
            SUM(dt.produced) AS total_produced,
            SUM(dt.waste) AS total_waste,
            COUNT(DISTINCT dt.product_id) AS products
        FROM public.daily_throwaway dt
        WHERE dt.store_id = 1
          AND dt.date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY dt.date
        ORDER BY dt.date DESC
    """)
    
    dashboard_data = cur.fetchall()
    if dashboard_data:
        print(f"   ✅ Dashboard would show {len(dashboard_data)} days of data:")
        for day in dashboard_data:
            print(f"   - {day['date']}: waste={day['total_waste']}, products={day['products']}")
    else:
        print("   ❌ Dashboard query returns no data")
    
    # Step 5: Check for date type mismatches
    print("\n5️⃣  Checking date field types...")
    cur.execute("""
        SELECT 
            pws.submission_date, 
            pg_typeof(pws.submission_date) as submission_date_type
        FROM pending_waste_submissions pws
        LIMIT 1
    """)
    date_check = cur.fetchone()
    if date_check:
        print(f"   submission_date type: {date_check['submission_date_type']}")
    
    cur.execute("""
        SELECT 
            dt.date,
            pg_typeof(dt.date) as date_type
        FROM daily_throwaway dt
        LIMIT 1
    """)
    date_check2 = cur.fetchone()
    if date_check2:
        print(f"   daily_throwaway.date type: {date_check2['date_type']}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    
    cur.close()
    return_connection(conn)

if __name__ == "__main__":
    try:
        test_approval_flow()
    except Exception as e:
        print(f"\n❌ Error running diagnostic: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
