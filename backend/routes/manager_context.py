from flask import Blueprint, request, jsonify, abort
from ..models.db import get_connection

bp = Blueprint('manager_context', __name__, url_prefix='/api/v1/manager_context')


@bp.route('/', methods=['GET'])
def list_contexts():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM manager_context;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:context_id>', methods=['GET'])
def get_context(context_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM manager_context WHERE context_id=%s;', (context_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_context():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO manager_context (store_id, forecast_date, expected_busyness, reasons, notes, created_at) VALUES (%s,%s,%s,%s,%s,now()) RETURNING context_id;', (data.get('store_id'), data.get('forecast_date'), data.get('expected_busyness'), data.get('reasons'), data.get('notes')))
        cid = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'context_id': cid}), 201


@bp.route('/<int:context_id>', methods=['PUT'])
def update_context(context_id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE manager_context SET store_id=%s, forecast_date=%s, expected_busyness=%s, reasons=%s, notes=%s WHERE context_id=%s;', (data.get('store_id'), data.get('forecast_date'), data.get('expected_busyness'), data.get('reasons'), data.get('notes'), context_id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:context_id>', methods=['DELETE'])
def delete_context(context_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM manager_context WHERE context_id=%s;', (context_id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
