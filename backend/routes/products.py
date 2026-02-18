from flask import Blueprint, jsonify, request
from models.product_model import get_all_products
from models.db import get_connection, return_connection

products_bp = Blueprint("products", __name__)

@products_bp.get("/list")
def list_products():
    products = get_all_products()
    return jsonify(products)

@products_bp.post("/create")
def create_product():
    """Create a new product. Auto-detects type based on name."""
    data = request.get_json()
    
    if not data or not data.get("product_name"):
        return jsonify({"error": "product_name required"}), 400
    
    product_name = data["product_name"].strip()
    
    if not product_name:
        return jsonify({"error": "product_name cannot be empty"}), 400
    
    # Auto-detect product type based on name
    name_lower = product_name.lower()
    if "munchkin" in name_lower:
        product_type = "munchkin"
    elif any(word in name_lower for word in ["donut", "doughnut"]):
        product_type = "donut"
    elif "muffin" in name_lower:
        product_type = "muffin"
    elif "bagel" in name_lower:
        product_type = "bagel"
    elif any(word in name_lower for word in ["croissant", "danish", "scone", "pastry"]):
        product_type = "bakery"
    else:
        product_type = "other"
    
    try:
        conn = get_connection()
        try:
            cur = conn.cursor()
            
            # Check if product already exists
            cur.execute("""
                SELECT product_id FROM products 
                WHERE LOWER(product_name) = LOWER(%s)
            """, (product_name,))
            
            existing = cur.fetchone()
            if existing:
                cur.close()
                return jsonify({"error": "Product already exists"}), 409
            
            # Create new product
            cur.execute("""
                INSERT INTO products (product_name, product_type, is_active)
                VALUES (%s, %s, TRUE)
                RETURNING product_id, product_name, product_type, is_active
            """, (product_name, product_type))
            
            result = cur.fetchone()
            conn.commit()
            cur.close()
            
            return jsonify({
                "status": "success",
                "product": {
                    "product_id": result[0],
                    "product_name": result[1],
                    "product_type": result[2],
                    "is_active": result[3]
                }
            }), 201
        finally:
            return_connection(conn)
            
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

