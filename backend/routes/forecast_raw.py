from flask import Blueprint, request, jsonify, abort
from models.db import get_connection, return_connection

bp = Blueprint('forecast_raw', __name__, url_prefix='/api/v1/forecast')

# Support both /api/v1/forecast and /api/v1/forecast_raw for compatibility
bp_alt = Blueprint('forecast_raw_alt', __name__, url_prefix='/api/v1/forecast_raw')


@bp.route('/', methods=['GET'])
@bp_alt.route('/', methods=['GET'])
def list_raw():
    """Get forecast predictions - supports query params"""
    store_id = request.args.get('store_id', type=int)
    target_date = request.args.get('target_date', type=str)
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if store_id and target_date:
                cur.execute('SELECT * FROM forecast_raw WHERE store_id=%s AND forecast_date=%s;', (store_id, target_date))
            elif store_id:
                cur.execute('SELECT * FROM forecast_raw WHERE store_id=%s ORDER BY forecast_date DESC LIMIT 10;', (store_id,))
            else:
                cur.execute('SELECT * FROM forecast_raw ORDER BY forecast_date DESC LIMIT 100;')
            rows = cur.fetchall()
        
        # Convert rows to list of dicts if using RealDictCursor, otherwise format as needed
        result = []
        if rows:
            if isinstance(rows[0], dict):
                result = rows
            else:
                # Handle tuple results - would need to know column names
                result = [{"message": "No forecast data available"}] if not rows else rows
        
        return jsonify(result) if result else jsonify({"error": "No forecast found"}), 200 if result else 404
    finally:
        return_connection(conn)


@bp.route('/<int:forecast_id>', methods=['GET'])
@bp_alt.route('/<int:forecast_id>', methods=['GET'])
def get_raw(forecast_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM forecast_raw WHERE forecast_id=%s;', (forecast_id,))
            row = cur.fetchone()
        if not row:
            abort(404)
        return jsonify(row), 200
    finally:
        return_connection(conn)


@bp.route('/', methods=['POST'])
@bp_alt.route('/', methods=['POST'])
@bp.route('/raw', methods=['POST'])
@bp_alt.route('/raw', methods=['POST'])
def create_raw():
    data = request.get_json() or {}
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO forecast_raw (store_id, product_id, forecast_date, predicted_quantity, model_version, created_at) VALUES (%s,%s,%s,%s,%s,now()) RETURNING forecast_id;', (data.get('store_id'), data.get('product_id'), data.get('forecast_date'), data.get('predicted_quantity'), data.get('model_version')))
            fid = cur.fetchone()[0]
            conn.commit()
        return jsonify({'forecast_id': fid}), 201
    finally:
        return_connection(conn)


@bp.route('/<int:forecast_id>', methods=['PUT'])
@bp_alt.route('/<int:forecast_id>', methods=['PUT'])
def update_raw(forecast_id):
    data = request.get_json() or {}
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE forecast_raw SET store_id=%s, product_id=%s, forecast_date=%s, predicted_quantity=%s, model_version=%s WHERE forecast_id=%s;', (data.get('store_id'), data.get('product_id'), data.get('forecast_date'), data.get('predicted_quantity'), data.get('model_version'), forecast_id))
            conn.commit()
        return jsonify({'status':'updated'}), 200
    finally:
        return_connection(conn)


@bp.route('/<int:forecast_id>', methods=['DELETE'])
@bp_alt.route('/<int:forecast_id>', methods=['DELETE'])
def delete_raw(forecast_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM forecast_raw WHERE forecast_id=%s;', (forecast_id,))
            conn.commit()
        return jsonify({'status':'deleted'}), 200
    finally:
        return_connection(conn)
