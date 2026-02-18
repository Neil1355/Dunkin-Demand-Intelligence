from flask import Blueprint, request, jsonify, abort
from models.db import get_connection, return_connection

bp = Blueprint('daily_production', __name__, url_prefix='/api/v1/daily_production')


@bp.route('/', methods=['GET'])
def list_production():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM daily_production;')
            rows = cur.fetchall()
        return jsonify(rows), 200
    finally:
        return_connection(conn)


@bp.route('/<int:id>', methods=['GET'])
def get_production(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM daily_production WHERE id=%s;', (id,))
            row = cur.fetchone()
        if not row:
            abort(404)
        return jsonify(row), 200
    finally:
        return_connection(conn)


@bp.route('/', methods=['POST'])
def create_production():
    data = request.get_json() or {}
    cols = ('store_id','product_id','date','quantity','source','created_at','updated_at')
    vals = tuple(data.get(c) for c in cols)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO daily_production (store_id,product_id,date,quantity,source,created_at,updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id;', vals)
            new_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({'id': new_id}), 201
    finally:
        return_connection(conn)


@bp.route('/<int:id>', methods=['PUT'])
def update_production(id):
    data = request.get_json() or {}
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE daily_production SET store_id=%s, product_id=%s, date=%s, quantity=%s, source=%s, updated_at=now() WHERE id=%s;', (data.get('store_id'), data.get('product_id'), data.get('date'), data.get('quantity'), data.get('source'), id))
            conn.commit()
        return jsonify({'status':'updated'}), 200
    finally:
        return_connection(conn)


@bp.route('/<int:id>', methods=['DELETE'])
def delete_production(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM daily_production WHERE id=%s;', (id,))
            conn.commit()
        return jsonify({'status':'deleted'}), 200
    finally:
        return_connection(conn)
