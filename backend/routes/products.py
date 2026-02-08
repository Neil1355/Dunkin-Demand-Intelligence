from flask import Blueprint, jsonify
from models.product_model import get_all_products

products_bp = Blueprint("products", __name__)

@products_bp.get("/list")
def list_products():
    products = get_all_products()
    return jsonify(products)
