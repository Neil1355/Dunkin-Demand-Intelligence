from flask import Blueprint, request, jsonify, abort
from models.db import get_connection, return_connection

bp = Blueprint('calendar_events', __name__, url_prefix='/api/v1/calendar_events')


@bp.route('/', methods=['GET'])
def list_events():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM calendar_events;')
        rows = cur.fetchall()
    return_connection(conn)
    return jsonify(rows), 200


@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM calendar_events WHERE event_id=%s;', (event_id,))
        row = cur.fetchone()
    return_connection(conn)
    if not row:
        abort(404)
    return jsonify(row), 200


@bp.route('/', methods=['POST'])
def create_event():
    data = request.get_json() or {}
    cols = ('event_id', 'event_date', 'event_name', 'multiplier')
    vals = tuple(data.get(c) for c in cols)
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO calendar_events (event_id, event_date, event_name, multiplier) VALUES (%s,%s,%s,%s);', vals)
        conn.commit()
    return_connection(conn)
    return jsonify({'status':'success'}), 201


@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json() or {}
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('UPDATE calendar_events SET event_date=%s, event_name=%s, multiplier=%s WHERE event_id=%s;', (data.get('event_date'), data.get('event_name'), data.get('multiplier'), event_id))
        conn.commit()
    return_connection(conn)
    return jsonify({'status':'updated'}), 200


@bp.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM calendar_events WHERE event_id=%s;', (event_id,))
        conn.commit()
    return_connection(conn)
    return jsonify({'status':'deleted'}), 200
