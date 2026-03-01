"""
Pending Waste Submissions Management Routes (Manager - Auth Required)
Allows managers to view, approve, edit, or discard employee waste submissions
"""
from flask import Blueprint, jsonify, request, g
import traceback
from models.db import get_connection, return_connection
from utils.jwt_handler import require_auth
from datetime import datetime, date

pending_waste_bp = Blueprint("pending_waste", __name__, url_prefix="/api/v1/pending-waste")


@pending_waste_bp.route("/list", methods=["GET"])
@require_auth
def get_pending_submissions():
    """
    Get list of pending waste submissions for a store
    Query params:
    - store_id (required): Filter by store
    - status (optional): Filter by status (pending/approved/edited/discarded), default: pending
    - date (optional): Filter by submission date (YYYY-MM-DD)
    """
    try:
        user_id = g.user_id  # Set by @require_auth decorator
        store_id = request.args.get('store_id', type=int)
        status = request.args.get('status', 'pending')
        submission_date = request.args.get('date')
        
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400
        
        # TODO: Add store access validation (user can only see their stores)
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                # Build query based on filters
                if submission_date:
                    cur.execute('''
                        SELECT 
                            id, store_id, submitter_name, donut_count, munchkin_count, 
                            other_count, notes, submission_date, submitted_at, status,
                            reviewed_by, reviewed_at
                        FROM pending_waste_submissions
                        WHERE store_id = %s AND status = %s AND submission_date = %s
                        ORDER BY submitted_at DESC
                    ''', (store_id, status, submission_date))
                else:
                    cur.execute('''
                        SELECT 
                            id, store_id, submitter_name, donut_count, munchkin_count, 
                            other_count, notes, submission_date, submitted_at, status,
                            reviewed_by, reviewed_at
                        FROM pending_waste_submissions
                        WHERE store_id = %s AND status = %s
                        ORDER BY submitted_at DESC
                        LIMIT 100
                    ''', (store_id, status))
                
                rows = cur.fetchall()
                
                # Convert to list of dicts
                submissions = []
                for row in rows:
                    if isinstance(row, dict) or hasattr(row, "keys"):
                        row_dict = dict(row)
                        submissions.append({
                            "id": row_dict.get("id"),
                            "store_id": row_dict.get("store_id"),
                            "submitter_name": row_dict.get("submitter_name"),
                            "donut_count": row_dict.get("donut_count"),
                            "munchkin_count": row_dict.get("munchkin_count"),
                            "other_count": row_dict.get("other_count"),
                            "notes": row_dict.get("notes"),
                            "submission_date": row_dict.get("submission_date").isoformat() if row_dict.get("submission_date") and hasattr(row_dict.get("submission_date"), 'isoformat') else str(row_dict.get("submission_date")) if row_dict.get("submission_date") else None,
                            "submitted_at": row_dict.get("submitted_at").isoformat() if row_dict.get("submitted_at") and hasattr(row_dict.get("submitted_at"), 'isoformat') else str(row_dict.get("submitted_at")) if row_dict.get("submitted_at") else None,
                            "status": row_dict.get("status"),
                            "reviewed_by": row_dict.get("reviewed_by"),
                            "reviewed_at": row_dict.get("reviewed_at").isoformat() if row_dict.get("reviewed_at") and hasattr(row_dict.get("reviewed_at"), 'isoformat') else str(row_dict.get("reviewed_at")) if row_dict.get("reviewed_at") else None
                        })
                    else:
                        submissions.append({
                            "id": row[0],
                            "store_id": row[1],
                            "submitter_name": row[2],
                            "donut_count": row[3],
                            "munchkin_count": row[4],
                            "other_count": row[5],
                            "notes": row[6],
                            "submission_date": row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7]),
                            "submitted_at": row[8].isoformat() if hasattr(row[8], 'isoformat') else str(row[8]),
                            "status": row[9],
                            "reviewed_by": row[10],
                            "reviewed_at": row[11].isoformat() if row[11] and hasattr(row[11], 'isoformat') else str(row[11]) if row[11] else None
                        })
                
                # Attach item-level details for each submission
                submission_ids = [s["id"] for s in submissions if s.get("id")]
                items_by_submission = {}
                if submission_ids:
                    try:
                        submission_id_tuple = tuple(submission_ids)
                        cur.execute('''
                            SELECT submission_id, product_id, product_name, product_type, waste_quantity
                            FROM pending_waste_items
                            WHERE submission_id IN %s
                            ORDER BY submission_id, product_name
                        ''', (submission_id_tuple,))
                        item_rows = cur.fetchall()

                        for item in item_rows:
                            if isinstance(item, dict) or hasattr(item, "keys"):
                                item_dict = dict(item)
                                submission_id = item_dict.get("submission_id")
                                item_payload = {
                                    "product_id": item_dict.get("product_id"),
                                    "product_name": item_dict.get("product_name"),
                                    "product_type": item_dict.get("product_type"),
                                    "waste_quantity": item_dict.get("waste_quantity")
                                }
                            else:
                                submission_id = item[0]
                                item_payload = {
                                    "product_id": item[1],
                                    "product_name": item[2],
                                    "product_type": item[3],
                                    "waste_quantity": item[4]
                                }

                            items_by_submission.setdefault(submission_id, []).append(item_payload)
                    except Exception as item_error:
                        print(f"Warning: Could not load pending waste items: {item_error}")

                for submission in submissions:
                    submission["items"] = items_by_submission.get(submission.get("id"), [])
                
                return jsonify({
                    "success": True,
                    "store_id": store_id,
                    "status": status,
                    "count": len(submissions),
                    "submissions": submissions
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error fetching pending submissions: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch submissions"}), 500


@pending_waste_bp.route("/counts", methods=["GET"])
@require_auth
def get_pending_counts():
    """
    Get count of pending submissions by status for a store
    Useful for dashboard badges
    """
    try:
        store_id = request.args.get('store_id', type=int)
        
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT status, COUNT(*) as count
                    FROM pending_waste_submissions
                    WHERE store_id = %s
                    GROUP BY status
                ''', (store_id,))
                
                rows = cur.fetchall()
                
                counts = {}
                for row in rows:
                    if isinstance(row, dict):
                        counts[row['status']] = row['count']
                    else:
                        counts[row[0]] = row[1]
                
                return jsonify({
                    "success": True,
                    "store_id": store_id,
                    "counts": counts,
                    "pending": counts.get('pending', 0),
                    "approved": counts.get('approved', 0),
                    "edited": counts.get('edited', 0),
                    "discarded": counts.get('discarded', 0)
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error fetching pending counts: {e}")
        return jsonify({"error": "Failed to fetch counts"}), 500


@pending_waste_bp.route("/approve", methods=["POST"])
@require_auth
def approve_submission():
    """
    Approve a pending submission (accept as-is)
    Moves data to daily_waste table
    
    Request body:
    {
        "submission_id": 123
    }
    """
    try:
        user_id = g.user_id  # Set by @require_auth decorator
        try:
            reviewer_id = int(user_id) if user_id is not None else None
        except (ValueError, TypeError):
            reviewer_id = None
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        submission_id = data.get('submission_id')
        
        if not submission_id:
            return jsonify({"error": "submission_id is required"}), 400
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                # Get submission details
                cur.execute('''
                    SELECT store_id, submitter_name, donut_count, munchkin_count, 
                           other_count, notes, submission_date, status
                    FROM pending_waste_submissions
                    WHERE id = %s
                ''', (submission_id,))
                
                submission = cur.fetchone()
                
                if not submission:
                    return jsonify({"error": "Submission not found"}), 404
                
                if isinstance(submission, dict):
                    status = submission['status']
                    store_id = submission['store_id']
                    donut_count = submission['donut_count']
                    munchkin_count = submission['munchkin_count']
                    other_count = submission['other_count']
                    submission_date = submission['submission_date']
                else:
                    status = submission[7]
                    store_id = submission[0]
                    donut_count = submission[2]
                    munchkin_count = submission[3]
                    other_count = submission[4]
                    submission_date = submission[6]
                
                if status != 'pending':
                    return jsonify({"error": f"Submission is already {status}"}), 400
                
                # TODO: Add validation that user has access to this store
                
                # Mark as approved
                cur.execute('''
                    UPDATE pending_waste_submissions
                    SET status = 'approved',
                        reviewed_by = %s,
                        reviewed_at = NOW()
                    WHERE id = %s
                ''', (reviewer_id, submission_id))
                
                # Get items from pending_waste_items to insert into daily_throwaway
                cur.execute('''
                    SELECT product_id, product_name, product_type, waste_quantity
                    FROM pending_waste_items
                    WHERE submission_id = %s
                ''', (submission_id,))
                
                items = cur.fetchall()
                print(f"[APPROVE DEBUG] Found {len(items)} items to insert into daily_throwaway", flush=True)
                print(f"[APPROVE DEBUG] Store ID: {store_id}, Submission Date: {submission_date}", flush=True)
                
                # Insert each item into daily_throwaway table (per-product tracking)
                cur.execute("SAVEPOINT pending_approve_daily_throwaway")
                try:
                    inserted_count = 0
                    updated_count = 0
                    skipped_count = 0
                    
                    for item in items:
                        if isinstance(item, dict):
                            product_id = item['product_id']
                            product_name = item['product_name']
                            waste_qty = item['waste_quantity']
                        else:
                            product_id = item[0]
                            product_name = item[1]
                            waste_qty = item[3]
                        
                        print(f"[APPROVE DEBUG] Processing: product_id={product_id}, name={product_name}, waste={waste_qty}", flush=True)
                        
                        # Only insert if we have a valid product_id (skip custom items without ID)
                        if product_id:
                            # Check if record exists
                            cur.execute('''
                                SELECT id, waste FROM daily_throwaway
                                WHERE store_id = %s AND product_id = %s AND date = %s
                            ''', (store_id, product_id, submission_date))
                            
                            existing = cur.fetchone()
                            
                            if existing:
                                # Update existing record
                                existing_waste = existing[1] if not isinstance(existing, dict) else existing['waste']
                                print(f"[APPROVE DEBUG] Updating existing record: id={existing[0] if not isinstance(existing, dict) else existing['id']}, old_waste={existing_waste}, adding={waste_qty}", flush=True)
                                cur.execute('''
                                    UPDATE daily_throwaway
                                    SET waste = %s, updated_at = NOW()
                                    WHERE store_id = %s AND product_id = %s AND date = %s
                                ''', (existing_waste + waste_qty, store_id, product_id, submission_date))
                                updated_count += 1
                            else:
                                # Insert new record
                                print(f"[APPROVE DEBUG] Inserting new record for product_id={product_id}, waste={waste_qty}", flush=True)
                                cur.execute('''
                                    INSERT INTO daily_throwaway 
                                    (store_id, product_id, date, waste, source, produced)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                ''', (store_id, product_id, submission_date, waste_qty, 'pending_approval', 0))
                                inserted_count += 1
                        else:
                            print(f"[APPROVE DEBUG] Skipping custom item without product_id: {product_name}", flush=True)
                            skipped_count += 1
                    
                    print(f"[APPROVE DEBUG] Summary: inserted={inserted_count}, updated={updated_count}, skipped={skipped_count}", flush=True)
                    cur.execute("RELEASE SAVEPOINT pending_approve_daily_throwaway")
                except Exception as insert_error:
                    print(f"[APPROVE ERROR] Failed to insert into daily_throwaway: {insert_error}", flush=True)
                    import traceback
                    traceback.print_exc()
                    cur.execute("ROLLBACK TO SAVEPOINT pending_approve_daily_throwaway")
                    cur.execute("RELEASE SAVEPOINT pending_approve_daily_throwaway")
                    print(f"Warning: Could not insert into daily_throwaway: {insert_error}", flush=True)
                    # Continue anyway - approval still recorded
                
                conn.commit()
                print(f"[APPROVE DEBUG] Transaction committed successfully", flush=True)
                
                return jsonify({
                    "success": True,
                    "message": "Submission approved and added to daily waste",
                    "submission_id": submission_id
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error approving submission: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to approve submission"}), 500


@pending_waste_bp.route("/edit-and-save", methods=["POST"])
@require_auth
def edit_and_save_submission():
    """
    Edit counts and approve submission
    
    Request body:
    {
        "submission_id": 123,
        "donut_count": 25,
        "munchkin_count": 10,
        "other_count": 3,
        "notes": "Adjusted - extra waste found"
    }
    """
    try:
        user_id = g.user_id  # Set by @require_auth decorator
        try:
            reviewer_id = int(user_id) if user_id is not None else None
        except (ValueError, TypeError):
            reviewer_id = None
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        submission_id = data.get('submission_id')
        donut_count = data.get('donut_count')
        munchkin_count = data.get('munchkin_count')
        other_count = data.get('other_count', 0)
        notes = data.get('notes', '').strip()
        items = data.get('items')
        
        if not submission_id:
            return jsonify({"error": "submission_id is required"}), 400
        
        # Validate / derive counts
        validated_items = []
        if isinstance(items, list) and len(items) > 0:
            donut_count = 0
            munchkin_count = 0
            other_count = 0

            for item in items:
                if not isinstance(item, dict):
                    return jsonify({"error": "Invalid items payload"}), 400

                product_name = (item.get('product_name') or '').strip()
                product_type = (item.get('product_type') or 'other').strip().lower()
                product_id = item.get('product_id')

                try:
                    waste_quantity = int(item.get('waste_quantity', 0))
                except (ValueError, TypeError):
                    return jsonify({"error": "Invalid item quantity"}), 400

                if waste_quantity < 0:
                    return jsonify({"error": "Item quantities cannot be negative"}), 400

                if product_type == 'donut':
                    donut_count += waste_quantity
                elif product_type == 'munchkin':
                    munchkin_count += waste_quantity
                else:
                    other_count += waste_quantity

                if product_name:
                    validated_items.append({
                        'product_id': product_id,
                        'product_name': product_name,
                        'product_type': product_type,
                        'waste_quantity': waste_quantity
                    })
        else:
            try:
                donut_count = int(donut_count) if donut_count is not None else 0
                munchkin_count = int(munchkin_count) if munchkin_count is not None else 0
                other_count = int(other_count) if other_count else 0

                if donut_count < 0 or munchkin_count < 0 or other_count < 0:
                    return jsonify({"error": "Counts cannot be negative"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid count values"}), 400
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                # Get submission
                cur.execute('''
                    SELECT store_id, submission_date, status
                    FROM pending_waste_submissions
                    WHERE id = %s
                ''', (submission_id,))
                
                submission = cur.fetchone()
                
                if not submission:
                    return jsonify({"error": "Submission not found"}), 404
                
                if isinstance(submission, dict):
                    status = submission['status']
                    store_id = submission['store_id']
                    submission_date = submission['submission_date']
                else:
                    status = submission[2]
                    store_id = submission[0]
                    submission_date = submission[1]
                
                if status != 'pending':
                    return jsonify({"error": f"Submission is already {status}"}), 400
                
                # Update submission with edited values
                cur.execute('''
                    UPDATE pending_waste_submissions
                    SET donut_count = %s,
                        munchkin_count = %s,
                        other_count = %s,
                        notes = %s,
                        status = 'edited',
                        reviewed_by = %s,
                        reviewed_at = NOW()
                    WHERE id = %s
                ''', (donut_count, munchkin_count, other_count, notes, reviewer_id, submission_id))

                # Update item-level details when provided
                if isinstance(items, list):
                    cur.execute('''
                        DELETE FROM pending_waste_items
                        WHERE submission_id = %s
                    ''', (submission_id,))

                    if validated_items:
                        for item in validated_items:
                            cur.execute('''
                                INSERT INTO pending_waste_items
                                (submission_id, product_id, product_name, product_type, waste_quantity)
                                VALUES (%s, %s, %s, %s, %s)
                            ''', (
                                submission_id,
                                item['product_id'],
                                item['product_name'],
                                item['product_type'],
                                item['waste_quantity']
                            ))
                
                # Insert into daily_throwaway table (per-product tracking)
                cur.execute("SAVEPOINT pending_edit_daily_throwaway")
                try:
                    # Get updated items to insert into daily_throwaway
                    cur.execute('''
                        SELECT product_id, product_name, waste_quantity
                        FROM pending_waste_items
                        WHERE submission_id = %s AND product_id IS NOT NULL
                    ''', (submission_id,))
                    
                    updated_items = cur.fetchall()
                    print(f"[EDIT DEBUG] Found {len(updated_items)} items to insert into daily_throwaway", flush=True)
                    print(f"[EDIT DEBUG] Store ID: {store_id}, Submission Date: {submission_date}", flush=True)
                    
                    inserted_count = 0
                    updated_count = 0
                    
                    for item in updated_items:
                        if isinstance(item, dict):
                            product_id = item['product_id']
                            product_name = item['product_name']
                            waste_qty = item['waste_quantity']
                        else:
                            product_id = item[0]
                            product_name = item[1]
                            waste_qty = item[2]
                        
                        print(f"[EDIT DEBUG] Processing: product_id={product_id}, name={product_name}, waste={waste_qty}", flush=True)
                        
                        # Check if record exists
                        cur.execute('''
                            SELECT id, waste FROM daily_throwaway
                            WHERE store_id = %s AND product_id = %s AND date = %s
                        ''', (store_id, product_id, submission_date))
                        
                        existing = cur.fetchone()
                        
                        if existing:
                            # Update existing record
                            existing_waste = existing[1] if not isinstance(existing, dict) else existing['waste']
                            print(f"[EDIT DEBUG] Updating existing record: old_waste={existing_waste}, adding={waste_qty}", flush=True)
                            cur.execute('''
                                UPDATE daily_throwaway
                                SET waste = %s, updated_at = NOW()
                                WHERE store_id = %s AND product_id = %s AND date = %s
                            ''', (existing_waste + waste_qty, store_id, product_id, submission_date))
                            updated_count += 1
                        else:
                            # Insert new record
                            print(f"[EDIT DEBUG] Inserting new record for product_id={product_id}, waste={waste_qty}", flush=True)
                            cur.execute('''
                                INSERT INTO daily_throwaway 
                                (store_id, product_id, date, waste, source, produced)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            ''', (store_id, product_id, submission_date, waste_qty, 'pending_approval', 0))
                            inserted_count += 1
                    
                    print(f"[EDIT DEBUG] Summary: inserted={inserted_count}, updated={updated_count}", flush=True)
                    cur.execute("RELEASE SAVEPOINT pending_edit_daily_throwaway")
                except Exception as insert_error:
                    print(f"[EDIT ERROR] Failed to insert into daily_throwaway: {insert_error}", flush=True)
                    import traceback
                    traceback.print_exc()
                    cur.execute("ROLLBACK TO SAVEPOINT pending_edit_daily_throwaway")
                    cur.execute("RELEASE SAVEPOINT pending_edit_daily_throwaway")
                    print(f"Warning: Could not insert into daily_throwaway: {insert_error}", flush=True)
                
                conn.commit()
                print(f"[EDIT DEBUG] Transaction committed successfully", flush=True)
                
                return jsonify({
                    "success": True,
                    "message": "Submission edited and saved to daily waste",
                    "submission_id": submission_id,
                    "donut_count": donut_count,
                    "munchkin_count": munchkin_count,
                    "other_count": other_count
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error editing submission: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to edit submission"}), 500


@pending_waste_bp.route("/discard", methods=["POST"])
@require_auth
def discard_submission():
    """
    Discard/reject a pending submission
    
    Request body:
    {
        "submission_id": 123,
        "reason": "Duplicate entry"  // Optional
    }
    """
    try:
        user_id = g.user_id  # Set by @require_auth decorator
        try:
            reviewer_id = int(user_id) if user_id is not None else None
        except (ValueError, TypeError):
            reviewer_id = None
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        submission_id = data.get('submission_id')
        reason = data.get('reason', '').strip()
        
        if not submission_id:
            return jsonify({"error": "submission_id is required"}), 400
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                # Check submission exists and is pending
                cur.execute('''
                    SELECT status FROM pending_waste_submissions
                    WHERE id = %s
                ''', (submission_id,))
                
                result = cur.fetchone()
                
                if not result:
                    return jsonify({"error": "Submission not found"}), 404
                
                status = result['status'] if isinstance(result, dict) else result[0]
                
                if status != 'pending':
                    return jsonify({"error": f"Submission is already {status}"}), 400
                
                # Mark as discarded
                cur.execute('''
                    UPDATE pending_waste_submissions
                    SET status = 'discarded',
                        reviewed_by = %s,
                        reviewed_at = NOW(),
                        notes = COALESCE(notes || E'\\n' || 'Discarded: ' || %s, 'Discarded: ' || %s)
                    WHERE id = %s
                ''', (reviewer_id, reason, reason, submission_id))
                
                conn.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Submission discarded",
                    "submission_id": submission_id
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error discarding submission: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to discard submission"}), 500
