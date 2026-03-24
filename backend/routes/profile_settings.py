from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection

forecast_settings_bp = Blueprint("forecast_settings", __name__)

DEFAULT_MULTIPLIERS = {
    "busy_multiplier": 1.18,
    "normal_multiplier": 1.00,
    "slow_multiplier": 0.86,
    "unsure_multiplier": 1.00,
    "festival_week_multiplier": 1.20,
    "festival_day_multiplier": 1.14,
    "snowstorm_multiplier": 0.72,
}


def ensure_settings_table(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS public.forecast_multiplier_settings (
            store_id INTEGER PRIMARY KEY REFERENCES stores(id) ON DELETE CASCADE,
            busy_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.18,
            normal_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
            slow_multiplier NUMERIC(5,2) NOT NULL DEFAULT 0.86,
            unsure_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
            festival_week_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.20,
            festival_day_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.14,
            snowstorm_multiplier NUMERIC(5,2) NOT NULL DEFAULT 0.72,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def clamp_multiplier(value: float) -> float:
    return max(0.5, min(2.0, value))


@forecast_settings_bp.get("/")
def get_forecast_settings():
    store_id = request.args.get("store_id", type=int)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_settings_table(cur)

        cur.execute(
            """
            SELECT
                fms.busy_multiplier,
                fms.normal_multiplier,
                fms.slow_multiplier,
                fms.unsure_multiplier,
                fms.festival_week_multiplier,
                fms.festival_day_multiplier,
                fms.snowstorm_multiplier,
                s.name AS store_name
            FROM stores s
            LEFT JOIN forecast_multiplier_settings fms ON fms.store_id = s.id
            WHERE s.id = %s
            LIMIT 1
            """,
            (store_id,),
        )
        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Store not found"}), 404

        settings = {
            key: float(row[key]) if row.get(key) is not None else default
            for key, default in DEFAULT_MULTIPLIERS.items()
        }

        return jsonify(
            {
                "store_id": store_id,
                "store_name": row.get("store_name"),
                "settings": settings,
            }
        ), 200
    finally:
        return_connection(conn)


@forecast_settings_bp.put("/")
def update_forecast_settings():
    data = request.get_json() or {}
    store_id = data.get("store_id")
    settings = data.get("settings") or {}

    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    payload = {}
    for key, default in DEFAULT_MULTIPLIERS.items():
        raw_value = settings.get(key, default)
        try:
            payload[key] = clamp_multiplier(float(raw_value))
        except (TypeError, ValueError):
            payload[key] = default

    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_settings_table(cur)

        cur.execute(
            """
            INSERT INTO forecast_multiplier_settings (
                store_id,
                busy_multiplier,
                normal_multiplier,
                slow_multiplier,
                unsure_multiplier,
                festival_week_multiplier,
                festival_day_multiplier,
                snowstorm_multiplier,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (store_id)
            DO UPDATE SET
                busy_multiplier = EXCLUDED.busy_multiplier,
                normal_multiplier = EXCLUDED.normal_multiplier,
                slow_multiplier = EXCLUDED.slow_multiplier,
                unsure_multiplier = EXCLUDED.unsure_multiplier,
                festival_week_multiplier = EXCLUDED.festival_week_multiplier,
                festival_day_multiplier = EXCLUDED.festival_day_multiplier,
                snowstorm_multiplier = EXCLUDED.snowstorm_multiplier,
                updated_at = NOW()
            """,
            (
                store_id,
                payload["busy_multiplier"],
                payload["normal_multiplier"],
                payload["slow_multiplier"],
                payload["unsure_multiplier"],
                payload["festival_week_multiplier"],
                payload["festival_day_multiplier"],
                payload["snowstorm_multiplier"],
            ),
        )

        conn.commit()

        return jsonify({"message": "Forecast settings updated", "settings": payload}), 200
    finally:
        return_connection(conn)


@forecast_settings_bp.post("/reset")
def reset_forecast_settings():
    data = request.get_json() or {}
    store_id = data.get("store_id")

    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_settings_table(cur)

        cur.execute(
            """
            INSERT INTO forecast_multiplier_settings (
                store_id,
                busy_multiplier,
                normal_multiplier,
                slow_multiplier,
                unsure_multiplier,
                festival_week_multiplier,
                festival_day_multiplier,
                snowstorm_multiplier,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (store_id)
            DO UPDATE SET
                busy_multiplier = EXCLUDED.busy_multiplier,
                normal_multiplier = EXCLUDED.normal_multiplier,
                slow_multiplier = EXCLUDED.slow_multiplier,
                unsure_multiplier = EXCLUDED.unsure_multiplier,
                festival_week_multiplier = EXCLUDED.festival_week_multiplier,
                festival_day_multiplier = EXCLUDED.festival_day_multiplier,
                snowstorm_multiplier = EXCLUDED.snowstorm_multiplier,
                updated_at = NOW()
            """,
            (
                store_id,
                DEFAULT_MULTIPLIERS["busy_multiplier"],
                DEFAULT_MULTIPLIERS["normal_multiplier"],
                DEFAULT_MULTIPLIERS["slow_multiplier"],
                DEFAULT_MULTIPLIERS["unsure_multiplier"],
                DEFAULT_MULTIPLIERS["festival_week_multiplier"],
                DEFAULT_MULTIPLIERS["festival_day_multiplier"],
                DEFAULT_MULTIPLIERS["snowstorm_multiplier"],
            ),
        )

        conn.commit()

        return jsonify({"message": "Forecast settings reset", "settings": DEFAULT_MULTIPLIERS}), 200
    finally:
        return_connection(conn)
