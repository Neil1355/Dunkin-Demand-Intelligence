from flask import Blueprint, request, jsonify, abort
from ..models.db import get_connection

bp = Blueprint('forecast_history', __name__, url_prefix='/api/v1/forecast_history')


@bp.route('/', methods=['GET'])
def list_history():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM forecast_history;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/query', methods=['GET'])
def get_history():
    # query by composite key via query params
    store_id = request.args.get('store_id')
    product_id = request.args.get('product_id')
    forecast_date = request.args.get('forecast_date')
    target_date = request.args.get('target_date')
    if not (store_id and product_id and forecast_date and target_date):
        return jsonify({'status':'error','message':'store_id, product_id, forecast_date, target_date required'}), 400
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM forecast_history WHERE store_id=%s AND product_id=%s AND forecast_date=%s AND target_date=%s;', (store_id, product_id, forecast_date, target_date))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_history():
    data = request.get_json() or {}
    cols = ('store_id','product_id','forecast_date','target_date','predicted_quantity','model_version','status','manager_override_quantity','confidence','notes','expectation','approved_by','approved_at','final_quantity','context_expectation','context_multiplier','adjusted_quantity','actual_sold','forecast_error','error_pct')
    vals = tuple(data.get(c) for c in cols)
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO forecast_history (store_id,product_id,forecast_date,target_date,predicted_quantity,model_version,created_at,status,manager_override_quantity,confidence,notes,expectation,approved_by,approved_at,final_quantity,context_expectation,context_multiplier,adjusted_quantity,actual_sold,forecast_error,error_pct) VALUES (%s,%s,%s,%s,%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', vals)
        conn.commit()
    conn.close()
    return jsonify({'status':'created'}), 201


@bp.route('/', methods=['PUT'])
def update_history():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE forecast_history SET predicted_quantity=%s, model_version=%s, status=%s, manager_override_quantity=%s, confidence=%s, notes=%s, expectation=%s, approved_by=%s, approved_at=%s, final_quantity=%s, context_expectation=%s, context_multiplier=%s, adjusted_quantity=%s, actual_sold=%s, forecast_error=%s, error_pct=%s WHERE store_id=%s AND product_id=%s AND forecast_date=%s AND target_date=%s;', (data.get('predicted_quantity'), data.get('model_version'), data.get('status'), data.get('manager_override_quantity'), data.get('confidence'), data.get('notes'), data.get('expectation'), data.get('approved_by'), data.get('approved_at'), data.get('final_quantity'), data.get('context_expectation'), data.get('context_multiplier'), data.get('adjusted_quantity'), data.get('actual_sold'), data.get('forecast_error'), data.get('error_pct'), data.get('store_id'), data.get('product_id'), data.get('forecast_date'), data.get('target_date')))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/', methods=['DELETE'])
def delete_history():
    store_id = request.args.get('store_id')
    product_id = request.args.get('product_id')
    forecast_date = request.args.get('forecast_date')
    target_date = request.args.get('target_date')
    if not (store_id and product_id and forecast_date and target_date):
        return jsonify({'status':'error','message':'store_id, product_id, forecast_date, target_date required'}), 400
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM forecast_history WHERE store_id=%s AND product_id=%s AND forecast_date=%s AND target_date=%s;', (store_id, product_id, forecast_date, target_date))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
