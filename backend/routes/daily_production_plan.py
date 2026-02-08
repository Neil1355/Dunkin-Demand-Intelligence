from flask import Blueprint, request, jsonify, abort
from models.db import get_connection

bp = Blueprint('daily_production_plan', __name__, url_prefix='/api/v1/daily_production_plan')


@bp.route('/', methods=['GET'])
def list_plans():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_production_plan;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/', methods=['POST'])
def create_plan():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO daily_production_plan (store_id, product_id, production_date, planned_quantity, source, created_at) VALUES (%s,%s,%s,%s,%s,now());', (data.get('store_id'), data.get('product_id'), data.get('production_date'), data.get('planned_quantity'), data.get('source')))
        conn.commit()
    conn.close()
    return jsonify({'status':'created'}), 201


@bp.route('/', methods=['PUT'])
def update_plan():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE daily_production_plan SET planned_quantity=%s, source=%s WHERE store_id=%s AND product_id=%s AND production_date=%s;', (data.get('planned_quantity'), data.get('source'), data.get('store_id'), data.get('product_id'), data.get('production_date')))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/', methods=['DELETE'])
def delete_plan():
    store_id = request.args.get('store_id')
    product_id = request.args.get('product_id')
    production_date = request.args.get('production_date')
    if not (store_id and product_id and production_date):
        return jsonify({'status':'error','message':'store_id, product_id and production_date are required'}), 400
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM daily_production_plan WHERE store_id=%s AND product_id=%s AND production_date=%s;', (store_id, product_id, production_date))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
