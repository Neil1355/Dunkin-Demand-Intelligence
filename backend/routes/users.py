from flask import Blueprint, request, jsonify, abort
from models.db import get_connection

bp = Blueprint('users', __name__, url_prefix='/api/v1/users')


@bp.route('/', methods=['GET'])
def list_users():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT id, name, email, created_at FROM users;')
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT id, name, email, created_at FROM users WHERE id=%s;', (id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_user_route():
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO users (name, email, created_at) VALUES (%s,%s,now()) RETURNING id;', (data.get('name'), data.get('email')))
        uid = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'id': uid}), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE users SET name=%s, email=%s WHERE id=%s;', (data.get('name'), data.get('email'), id))
        conn.commit()
    conn.close()
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM users WHERE id=%s;', (id,))
        conn.commit()
    conn.close()
    return jsonify({'status':'deleted'}), 200
