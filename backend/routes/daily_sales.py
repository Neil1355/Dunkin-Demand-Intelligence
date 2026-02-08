from flask import Blueprint, request, jsonify, abort
from ..models.db import get_connection

bp = Blueprint('daily_sales', __name__, url_prefix='/api/v1/daily_sales')


@bp.route('/', methods=['GET'])
def list_sales():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_sales;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_sales WHERE sale_id=%s;', (sale_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_sale():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO daily_sales (store_id, product_id, sale_date, quantity, source, created_at) VALUES (%s,%s,%s,%s,%s,now()) RETURNING sale_id;', (data.get('store_id'), data.get('product_id'), data.get('sale_date'), data.get('quantity'), data.get('source')))
        sale_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'sale_id': sale_id}), 201


@bp.route('/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE daily_sales SET store_id=%s, product_id=%s, sale_date=%s, quantity=%s, source=%s WHERE sale_id=%s;', (data.get('store_id'), data.get('product_id'), data.get('sale_date'), data.get('quantity'), data.get('source'), sale_id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM daily_sales WHERE sale_id=%s;', (sale_id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
