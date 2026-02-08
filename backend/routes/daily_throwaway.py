from flask import Blueprint, request, jsonify, abort
from ..models.db import get_connection

bp = Blueprint('daily_throwaway', __name__, url_prefix='/api/v1/daily_throwaway')


@bp.route('/', methods=['GET'])
def list_throwaways():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_throwaway;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:id>', methods=['GET'])
def get_throwaway(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM daily_throwaway WHERE id=%s;', (id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_throwaway():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO daily_throwaway (store_id, product_id, date, waste, source, created_at, updated_at, produced) VALUES (%s,%s,%s,%s,%s,now(),now(),%s) RETURNING id;', (data.get('store_id'), data.get('product_id'), data.get('date'), data.get('waste'), data.get('source'), data.get('produced')))
        new_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'id': new_id}), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_throwaway(id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE daily_throwaway SET store_id=%s, product_id=%s, date=%s, waste=%s, source=%s, updated_at=now(), produced=%s WHERE id=%s;', (data.get('store_id'), data.get('product_id'), data.get('date'), data.get('waste'), data.get('source'), data.get('produced'), id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:id>', methods=['DELETE'])
def delete_throwaway(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM daily_throwaway WHERE id=%s;', (id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
