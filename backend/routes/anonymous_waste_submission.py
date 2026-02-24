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
    Accessed via QR code scan at /waste?store_id=12345
    REQUIRES store PIN for security (anyone with store_id could submit otherwise)
    
    Request body:
    {
        "store_id": 12345,
        "store_pin": "1234",  // REQUIRED - all stores must have a PIN set for waste submission
        "submitter_name": "John Doe",
        "product_items": [       // Array of product-level waste
            {"product_id": 1, "product_name": "Glazed Donut", "product_type": "donut", "waste_quantity": 5},
            {"product_id": 2, "product_name": "Chocolate Frosted", "product_type": "donut", "waste_quantity": 3},
            {"product_id": -1, "product_name": "Custom Item", "product_type": "other", "waste_quantity": 2}
        ],
        "notes": "Extra waste from broken display"  // Optional
    }
    
    Note: product_type is 'donut', 'munchkin', 'bagel', 'bakery', 'muffin', or 'other'
    Custom items use negative IDs and allow user-defined product_type
    
    Security: PIN is MANDATORY to prevent unauthorized waste submissions from store_id tampering
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        store_id = data.get('store_id')
        submitter_name = data.get('submitter_name', '').strip()
        product_items = data.get('product_items', [])
        notes = data.get('notes', '').strip()
        store_pin = data.get('store_pin', '').strip()
        
        # Validate required fields
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400
        
        if not submitter_name:
            return jsonify({"error": "submitter_name is required"}), 400
        
        if len(submitter_name) < 2:
            return jsonify({"error": "Submitter name must be at least 2 characters"}), 400
        
        # Validate product items
        if not product_items or not isinstance(product_items, list) or len(product_items) == 0:
            return jsonify({"error": "At least one product item is required"}), 400
        
        # Validate each product item
        total_waste = 0
        valid_types = {'donut', 'munchkin', 'bagel', 'bakery', 'muffin', 'other'}
        for item in product_items:
            if not isinstance(item, dict):
                return jsonify({"error": "Invalid product item format"}), 400
            
            if 'product_id' not in item or 'product_name' not in item or 'waste_quantity' not in item:
                return jsonify({"error": "Each product item must have product_id, product_name, waste_quantity, and product_type"}), 400
            
            # Validate product_type
            product_type = item.get('product_type', 'other')
            if product_type not in valid_types:
                return jsonify({"error": f"Invalid product_type '{product_type}'. Must be one of: {', '.join(valid_types)}"}), 400
            
            try:
                waste_qty = int(item['waste_quantity'])
                if waste_qty < 0:
                    return jsonify({"error": f"Waste quantity cannot be negative for {item['product_name']}"}), 400
                if waste_qty > 0:
                    total_waste += waste_qty
            except (ValueError, TypeError):
                return jsonify({"error": f"Invalid waste quantity for {item['product_name']}"}), 400
        
        # Validate at least some waste was reported
        if total_waste == 0:
            return jsonify({"error": "At least one product must have waste quantity greater than 0"}), 400
        
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
                
                # PIN is MANDATORY - all stores must have one for waste submission to work
                if not stored_pin:
                    return jsonify({
                        "error": "Store is not set up for waste submission. Contact your store manager.",
                        "pin_required": True
                    }), 400
                
                if not store_pin:
                    return jsonify({"error": "Store PIN is required", "pin_required": True}), 401
                
                if store_pin != stored_pin:
                    return jsonify({"error": "Invalid store PIN", "pin_required": True}), 401
                
                # Get client info for audit
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
                # Insert pending submission (with placeholder counts for backward compatibility)
                cur.execute('''
                    INSERT INTO pending_waste_submissions 
                    (store_id, submitter_name, donut_count, munchkin_count, other_count, 
                     notes, submission_date, ip_address, user_agent, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                    RETURNING id, submitted_at
                ''', (store_id, submitter_name, 0, 0, 0,  # Counts set to 0, actual data in items table
                      notes, date.today(), ip_address, user_agent))
                
                result = cur.fetchone()
                submission_id = result['id'] if isinstance(result, dict) else result[0]
                submitted_at = result['submitted_at'] if isinstance(result, dict) else result[1]
                
                # Insert individual product items
                for item in product_items:
                    if int(item['waste_quantity']) > 0:  # Only insert non-zero items
                        product_type = item.get('product_type', 'other')  # Default to 'other' if not provided
                        cur.execute('''
                            INSERT INTO pending_waste_items 
                            (submission_id, product_id, product_name, product_type, waste_quantity)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (submission_id, item['product_id'], item['product_name'], product_type, item['waste_quantity']))
                
                conn.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Submission successful! Pending manager approval.",
                    "submission_id": submission_id,
                    "submitted_at": submitted_at.isoformat() if hasattr(submitted_at, 'isoformat') else str(submitted_at),
                    "store_id": store_id,
                    "submitter_name": submitter_name,
                    "product_items_count": len([i for i in product_items if int(i['waste_quantity']) > 0]),
                    "total_waste": total_waste
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


@anonymous_waste_bp.route("/products", methods=["GET"])
def get_products_for_waste():
    """
    Public endpoint to get list of all active products for waste submission
    No authentication required
    """
    try:
        conn = get_connection()
        
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT product_id, product_name, product_type, is_active
                    FROM products
                    WHERE is_active = true
                    ORDER BY 
                        CASE product_type
                            WHEN 'donut' THEN 1
                            WHEN 'munchkin' THEN 2
                            WHEN 'bagel' THEN 3
                            WHEN 'muffin' THEN 4
                            WHEN 'bakery' THEN 5
                            ELSE 6
                        END,
                        product_name
                ''')
                
                rows = cur.fetchall()
                
                # Convert to list of dicts
                products = []
                for row in rows:
                    if isinstance(row, dict):
                        products.append(row)
                    else:
                        products.append({
                            'product_id': row[0],
                            'product_name': row[1],
                            'product_type': row[2],
                            'is_active': row[3]
                        })
                
                return jsonify(products), 200
                
        finally:
            return_connection(conn)
            
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500
