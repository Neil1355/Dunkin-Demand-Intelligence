from flask import Blueprint, request, jsonify, abort
from models.db import get_connection

bp = Blueprint('daily_waste', __name__, url_prefix='/api/v1/daily_waste')


@bp.route('/', methods=['GET'])
def list_waste():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_waste;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:id>', methods=['GET'])
def get_waste(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_waste WHERE id=%s;', (id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_waste():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO daily_waste (id, store_id, entry_date, am_waste, pm_waste, total_waste, source, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,now());', (data.get('id'), data.get('store_id'), data.get('entry_date'), data.get('am_waste'), data.get('pm_waste'), data.get('total_waste'), data.get('source')))
        conn.commit()
    conn.close()
    return jsonify({'status':'created'}), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_waste(id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE daily_waste SET store_id=%s, entry_date=%s, am_waste=%s, pm_waste=%s, total_waste=%s, source=%s WHERE id=%s;', (data.get('store_id'), data.get('entry_date'), data.get('am_waste'), data.get('pm_waste'), data.get('total_waste'), data.get('source'), id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:id>', methods=['DELETE'])
def delete_waste(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM daily_waste WHERE id=%s;', (id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
