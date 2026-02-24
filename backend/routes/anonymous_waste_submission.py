"""
Anonymous Waste Submission Routes (Public - No Auth Required)
Allows employees to submit waste counts via QR code with optional PIN
Separate from the authenticated product-based waste submission system
"""
from flask import Blueprint, jsonify, request
from models.db import get_connection, return_connection
from datetime import datetime, date

anonymous_waste_bp = Blueprint("anonymous_waste", __name__, url_prefix="/api/v1/anonymous-waste")


@anonymous_waste_bp.route("/submit", methods=["POST"])
def submit_waste_anonymous():
    """
    Public endpoint for employees to submit waste counts via QR code
    No authentication required - uses store PIN for validation
    
    Request body:
    {
        "store_id": 12345,
        "store_pin": "1234",  // Optional - if store has PIN enabled
        "submitter_name": "John Doe",
        "donut_count": 24,
        "munchkin_count": 12,
        "other_count": 5,     // Optional
        "notes": "Extra waste from broken display"  // Optional
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        store_id = data.get('store_id')
        submitter_name = data.get('submitter_name', '').strip()
        donut_count = data.get('donut_count', 0)
        munchkin_count = data.get('munchkin_count', 0)
        other_count = data.get('other_count', 0)
        notes = data.get('notes', '').strip()
        store_pin = data.get('store_pin', '').strip()
        
        # Validate required fields
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400
        
        if not submitter_name:
            return jsonify({"error": "submitter_name is required"}), 400
        
        if len(submitter_name) < 2:
            return jsonify({"error": "Submitter name must be at least 2 characters"}), 400
        
        # Validate counts are non-negative
        try:
            donut_count = int(donut_count)
            munchkin_count = int(munchkin_count)
            other_count = int(other_count) if other_count else 0
            
            if donut_count < 0 or munchkin_count < 0 or other_count < 0:
                return jsonify({"error": "Counts cannot be negative"}), 400
                
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid count values"}), 400
        
        # Validate at least one count is provided
        if donut_count == 0 and munchkin_count == 0 and other_count == 0:
            return jsonify({"error": "At least one count must be greater than 0"}), 400
        
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                # Check if store exists and get PIN requirement
                cur.execute('SELECT id, store_pin FROM stores WHERE id = %s AND is_active = true', (store_id,))
                store = cur.fetchone()
                
                if not store:
                    return jsonify({"error": "Invalid store ID"}), 404
                
                # Validate PIN if store has one set
                stored_pin = store['store_pin'] if isinstance(store, dict) else store[1]
                
                if stored_pin:
                    if not store_pin:
                        return jsonify({"error": "Store PIN is required", "pin_required": True}), 401
                    
                    if store_pin != stored_pin:
                        return jsonify({"error": "Invalid store PIN", "pin_required": True}), 401
                
                # Get client info for audit
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
                # Insert pending submission
                cur.execute('''
                    INSERT INTO pending_waste_submissions 
                    (store_id, submitter_name, donut_count, munchkin_count, other_count, 
                     notes, submission_date, ip_address, user_agent, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                    RETURNING id, submitted_at
                ''', (store_id, submitter_name, donut_count, munchkin_count, other_count,
                      notes, date.today(), ip_address, user_agent))
                
                result = cur.fetchone()
                submission_id = result['id'] if isinstance(result, dict) else result[0]
                submitted_at = result['submitted_at'] if isinstance(result, dict) else result[1]
                
                conn.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Submission successful! Pending manager approval.",
                    "submission_id": submission_id,
                    "submitted_at": submitted_at.isoformat() if hasattr(submitted_at, 'isoformat') else str(submitted_at),
                    "store_id": store_id,
                    "submitter_name": submitter_name,
                    "donut_count": donut_count,
                    "munchkin_count": munchkin_count,
                    "other_count": other_count
                }), 201
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error in submit_waste_anonymous: {e}")
        return jsonify({"error": "Submission failed. Please try again."}), 500


@anonymous_waste_bp.route("/check-pin/<int:store_id>", methods=["GET"])
def check_pin_requirement(store_id):
    """
    Check if a store requires a PIN for submissions
    Public endpoint to help frontend show/hide PIN field
    """
    try:
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT store_pin FROM stores WHERE id = %s AND is_active = true', (store_id,))
                result = cur.fetchone()
                
                if not result:
                    return jsonify({"error": "Store not found"}), 404
                
                store_pin = result['store_pin'] if isinstance(result, dict) else result[0]
                pin_required = bool(store_pin)
                
                return jsonify({
                    "store_id": store_id,
                    "pin_required": pin_required
                }), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error checking PIN requirement: {e}")
        return jsonify({"error": "Failed to check PIN requirement"}), 500
