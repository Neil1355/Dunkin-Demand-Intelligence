from flask import Blueprint, request, jsonify, abort
from models.db import get_connection, return_connection

bp = Blueprint('forecast_raw', __name__, url_prefix='/api/v1/forecast_raw')


@bp.route('/', methods=['GET'])
def list_raw():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM forecast_raw;')
            rows = cur.fetchall()
        return jsonify(rows), 200
    finally:
        return_connection(conn)


@bp.route('/<int:forecast_id>', methods=['GET'])
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
def delete_raw(forecast_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM forecast_raw WHERE forecast_id=%s;', (forecast_id,))
            conn.commit()
        return jsonify({'status':'deleted'}), 200
    finally:
        return_connection(conn)
