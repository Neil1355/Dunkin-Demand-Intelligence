from flask import Blueprint, request, jsonify, abort
from ..models.db import get_connection

bp = Blueprint('forecast_final', __name__, url_prefix='/api/v1/forecast_final')


@bp.route('/', methods=['GET'])
def list_final():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM forecast_final;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:final_id>', methods=['GET'])
def get_final(final_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM forecast_final WHERE final_id=%s;', (final_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_final():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO forecast_final (store_id, product_id, forecast_date, predicted_quantity, final_quantity, was_edited, created_at) VALUES (%s,%s,%s,%s,%s,%s,now()) RETURNING final_id;', (data.get('store_id'), data.get('product_id'), data.get('forecast_date'), data.get('predicted_quantity'), data.get('final_quantity'), data.get('was_edited')))
        final_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'final_id': final_id}), 201


@bp.route('/<int:final_id>', methods=['PUT'])
def update_final(final_id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE forecast_final SET store_id=%s, product_id=%s, forecast_date=%s, predicted_quantity=%s, final_quantity=%s, was_edited=%s WHERE final_id=%s;', (data.get('store_id'), data.get('product_id'), data.get('forecast_date'), data.get('predicted_quantity'), data.get('final_quantity'), data.get('was_edited'), final_id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:final_id>', methods=['DELETE'])
def delete_final(final_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM forecast_final WHERE final_id=%s;', (final_id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
