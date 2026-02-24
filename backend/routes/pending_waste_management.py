"""
Pending Waste Submissions Management Routes (Manager - Auth Required)
Allows managers to view, approve, edit, or discard employee waste submissions
"""
from flask import Blueprint, jsonify, request
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
        user = request.user  # From JWT decorator
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
                    if isinstance(row, dict):
                        submissions.append(row)
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
        user = request.user
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
                ''', (user['user_id'], submission_id))
                
                # Insert into daily_waste table (if it exists)
                # Note: This assumes daily_waste table has these columns
                # Adjust based on your actual schema
                try:
                    cur.execute('''
                        INSERT INTO daily_waste 
                        (store_id, date, donut_waste, munchkin_waste, other_waste, notes)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (store_id, date) 
                        DO UPDATE SET 
                            donut_waste = daily_waste.donut_waste + EXCLUDED.donut_waste,
                            munchkin_waste = daily_waste.munchkin_waste + EXCLUDED.munchkin_waste,
                            other_waste = daily_waste.other_waste + EXCLUDED.other_waste,
                            notes = COALESCE(daily_waste.notes || E'\\n' || EXCLUDED.notes, EXCLUDED.notes)
                    ''', (store_id, submission_date, donut_count, munchkin_count, other_count, 
                          f"Submitted by: {submission[1] if not isinstance(submission, dict) else submission['submitter_name']}"))
                except Exception as insert_error:
                    print(f"Warning: Could not insert into daily_waste: {insert_error}")
                    # Continue anyway - approval still recorded
                
                conn.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Submission approved and added to daily waste",
                    "submission_id": submission_id
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error approving submission: {e}")
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
        user = request.user
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        submission_id = data.get('submission_id')
        donut_count = data.get('donut_count')
        munchkin_count = data.get('munchkin_count')
        other_count = data.get('other_count', 0)
        notes = data.get('notes', '').strip()
        
        if not submission_id:
            return jsonify({"error": "submission_id is required"}), 400
        
        # Validate counts
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
                ''', (donut_count, munchkin_count, other_count, notes, user['user_id'], submission_id))
                
                # Insert into daily_waste table
                try:
                    cur.execute('''
                        INSERT INTO daily_waste 
                        (store_id, date, donut_waste, munchkin_waste, other_waste, notes)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (store_id, date) 
                        DO UPDATE SET 
                            donut_waste = daily_waste.donut_waste + EXCLUDED.donut_waste,
                            munchkin_waste = daily_waste.munchkin_waste + EXCLUDED.munchkin_waste,
                            other_waste = daily_waste.other_waste + EXCLUDED.other_waste,
                            notes = COALESCE(daily_waste.notes || E'\\n' || EXCLUDED.notes, EXCLUDED.notes)
                    ''', (store_id, submission_date, donut_count, munchkin_count, other_count, notes))
                except Exception as insert_error:
                    print(f"Warning: Could not insert into daily_waste: {insert_error}")
                
                conn.commit()
                
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
        user = request.user
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
                ''', (user['user_id'], reason, reason, submission_id))
                
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
        return jsonify({"error": "Failed to discard submission"}), 500
