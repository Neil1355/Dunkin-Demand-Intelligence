from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection
import json

forecast_settings_bp = Blueprint("forecast_settings", __name__)

DEFAULT_MULTIPLIERS = {
    "busy_multiplier": 1.18,
    "normal_multiplier": 1.00,
    "slow_multiplier": 0.86,
    "unsure_multiplier": 1.00,
    "festival_week_multiplier": 1.20,
    "festival_day_multiplier": 1.14,
    "snowstorm_multiplier": 0.72,
    "target_waste_min_pct": 8.0,
    "target_waste_max_pct": 12.0,
    "auto_calendar_events_enabled": 1.0,
    "notify_in_app": 1.0,
    "notify_email": 0.0,
    "notify_forecast_shift": 1.0,
    "forecast_shift_threshold_pct": 12.0,
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
            target_waste_min_pct NUMERIC(5,2) NOT NULL DEFAULT 8.00,
            target_waste_max_pct NUMERIC(5,2) NOT NULL DEFAULT 12.00,
            auto_calendar_events_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            notify_in_app BOOLEAN NOT NULL DEFAULT TRUE,
            notify_email BOOLEAN NOT NULL DEFAULT FALSE,
            notify_forecast_shift BOOLEAN NOT NULL DEFAULT TRUE,
            forecast_shift_threshold_pct NUMERIC(5,2) NOT NULL DEFAULT 12.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Safe incremental evolution for existing databases.
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS target_waste_min_pct NUMERIC(5,2) NOT NULL DEFAULT 8.00;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS target_waste_max_pct NUMERIC(5,2) NOT NULL DEFAULT 12.00;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS auto_calendar_events_enabled BOOLEAN NOT NULL DEFAULT TRUE;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS notify_in_app BOOLEAN NOT NULL DEFAULT TRUE;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS notify_email BOOLEAN NOT NULL DEFAULT FALSE;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS notify_forecast_shift BOOLEAN NOT NULL DEFAULT TRUE;")
    cur.execute("ALTER TABLE public.forecast_multiplier_settings ADD COLUMN IF NOT EXISTS forecast_shift_threshold_pct NUMERIC(5,2) NOT NULL DEFAULT 12.00;")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS public.forecast_settings_history (
            history_id SERIAL PRIMARY KEY,
            store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
            changed_by TEXT,
            settings_json JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def clamp_multiplier(value: float) -> float:
    return max(0.5, min(2.0, value))


def clamp_waste_percent(value: float) -> float:
    return max(0.0, min(40.0, value))


def to_bool(raw, default=False):
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw != 0
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def normalize_settings(raw_settings: dict) -> dict:
    payload = {}
    for key, default in DEFAULT_MULTIPLIERS.items():
        raw_value = raw_settings.get(key, default)

        if key in ("target_waste_min_pct", "target_waste_max_pct", "forecast_shift_threshold_pct"):
            try:
                payload[key] = clamp_waste_percent(float(raw_value))
            except (TypeError, ValueError):
                payload[key] = default
            continue

        if key in ("auto_calendar_events_enabled", "notify_in_app", "notify_email", "notify_forecast_shift"):
            payload[key] = to_bool(raw_value, bool(default))
            continue

        try:
            payload[key] = clamp_multiplier(float(raw_value))
        except (TypeError, ValueError):
            payload[key] = default

    if payload["target_waste_min_pct"] > payload["target_waste_max_pct"]:
        payload["target_waste_min_pct"], payload["target_waste_max_pct"] = payload["target_waste_max_pct"], payload["target_waste_min_pct"]

    return payload


def write_settings_snapshot(cur, store_id: int, changed_by: str | None, settings_payload: dict):
    cur.execute(
        """
        INSERT INTO public.forecast_settings_history (store_id, changed_by, settings_json)
        VALUES (%s, %s, %s::jsonb)
        """,
        (store_id, changed_by, json.dumps(settings_payload)),
    )


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
                fms.target_waste_min_pct,
                fms.target_waste_max_pct,
                fms.auto_calendar_events_enabled,
                fms.notify_in_app,
                fms.notify_email,
                fms.notify_forecast_shift,
                fms.forecast_shift_threshold_pct,
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
            key: (bool(row[key]) if key in ("auto_calendar_events_enabled", "notify_in_app", "notify_email", "notify_forecast_shift") else float(row[key])) if row.get(key) is not None else default
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
    changed_by = data.get("changed_by")

    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    payload = normalize_settings(settings)

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
                target_waste_min_pct,
                target_waste_max_pct,
                auto_calendar_events_enabled,
                notify_in_app,
                notify_email,
                notify_forecast_shift,
                forecast_shift_threshold_pct,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (store_id)
            DO UPDATE SET
                busy_multiplier = EXCLUDED.busy_multiplier,
                normal_multiplier = EXCLUDED.normal_multiplier,
                slow_multiplier = EXCLUDED.slow_multiplier,
                unsure_multiplier = EXCLUDED.unsure_multiplier,
                festival_week_multiplier = EXCLUDED.festival_week_multiplier,
                festival_day_multiplier = EXCLUDED.festival_day_multiplier,
                snowstorm_multiplier = EXCLUDED.snowstorm_multiplier,
                target_waste_min_pct = EXCLUDED.target_waste_min_pct,
                target_waste_max_pct = EXCLUDED.target_waste_max_pct,
                auto_calendar_events_enabled = EXCLUDED.auto_calendar_events_enabled,
                notify_in_app = EXCLUDED.notify_in_app,
                notify_email = EXCLUDED.notify_email,
                notify_forecast_shift = EXCLUDED.notify_forecast_shift,
                forecast_shift_threshold_pct = EXCLUDED.forecast_shift_threshold_pct,
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
                payload["target_waste_min_pct"],
                payload["target_waste_max_pct"],
                payload["auto_calendar_events_enabled"],
                payload["notify_in_app"],
                payload["notify_email"],
                payload["notify_forecast_shift"],
                payload["forecast_shift_threshold_pct"],
            ),
        )

        write_settings_snapshot(cur, store_id, changed_by, payload)

        conn.commit()

        return jsonify({"message": "Forecast settings updated", "settings": payload}), 200
    finally:
        return_connection(conn)


@forecast_settings_bp.post("/reset")
def reset_forecast_settings():
    data = request.get_json() or {}
    store_id = data.get("store_id")
    changed_by = data.get("changed_by")

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
                target_waste_min_pct,
                target_waste_max_pct,
                auto_calendar_events_enabled,
                notify_in_app,
                notify_email,
                notify_forecast_shift,
                forecast_shift_threshold_pct,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (store_id)
            DO UPDATE SET
                busy_multiplier = EXCLUDED.busy_multiplier,
                normal_multiplier = EXCLUDED.normal_multiplier,
                slow_multiplier = EXCLUDED.slow_multiplier,
                unsure_multiplier = EXCLUDED.unsure_multiplier,
                festival_week_multiplier = EXCLUDED.festival_week_multiplier,
                festival_day_multiplier = EXCLUDED.festival_day_multiplier,
                snowstorm_multiplier = EXCLUDED.snowstorm_multiplier,
                target_waste_min_pct = EXCLUDED.target_waste_min_pct,
                target_waste_max_pct = EXCLUDED.target_waste_max_pct,
                auto_calendar_events_enabled = EXCLUDED.auto_calendar_events_enabled,
                notify_in_app = EXCLUDED.notify_in_app,
                notify_email = EXCLUDED.notify_email,
                notify_forecast_shift = EXCLUDED.notify_forecast_shift,
                forecast_shift_threshold_pct = EXCLUDED.forecast_shift_threshold_pct,
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
                DEFAULT_MULTIPLIERS["target_waste_min_pct"],
                DEFAULT_MULTIPLIERS["target_waste_max_pct"],
                DEFAULT_MULTIPLIERS["auto_calendar_events_enabled"],
                DEFAULT_MULTIPLIERS["notify_in_app"],
                DEFAULT_MULTIPLIERS["notify_email"],
                DEFAULT_MULTIPLIERS["notify_forecast_shift"],
                DEFAULT_MULTIPLIERS["forecast_shift_threshold_pct"],
            ),
        )

        write_settings_snapshot(cur, store_id, changed_by, DEFAULT_MULTIPLIERS)

        conn.commit()

        return jsonify({"message": "Forecast settings reset", "settings": DEFAULT_MULTIPLIERS}), 200
    finally:
        return_connection(conn)


@forecast_settings_bp.get("/history")
def get_settings_history():
    store_id = request.args.get("store_id", type=int)
    limit = request.args.get("limit", type=int, default=20)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_settings_table(cur)
        cur.execute(
            """
            SELECT history_id, changed_by, settings_json, created_at
            FROM public.forecast_settings_history
            WHERE store_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (store_id, max(1, min(limit, 100))),
        )
        rows = cur.fetchall()
        return jsonify({"history": rows}), 200
    finally:
        return_connection(conn)


@forecast_settings_bp.post("/rollback")
def rollback_settings():
    data = request.get_json() or {}
    store_id = data.get("store_id")
    history_id = data.get("history_id")
    changed_by = data.get("changed_by")

    if not store_id or not history_id:
        return jsonify({"error": "store_id and history_id required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        ensure_settings_table(cur)
        cur.execute(
            """
            SELECT settings_json
            FROM public.forecast_settings_history
            WHERE history_id = %s AND store_id = %s
            LIMIT 1
            """,
            (history_id, store_id),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "History snapshot not found"}), 404

        settings_json = row.get("settings_json") if isinstance(row, dict) else None
        if not settings_json:
            return jsonify({"error": "Invalid snapshot"}), 400

        payload = normalize_settings(settings_json)

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
                target_waste_min_pct,
                target_waste_max_pct,
                auto_calendar_events_enabled,
                notify_in_app,
                notify_email,
                notify_forecast_shift,
                forecast_shift_threshold_pct,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (store_id)
            DO UPDATE SET
                busy_multiplier = EXCLUDED.busy_multiplier,
                normal_multiplier = EXCLUDED.normal_multiplier,
                slow_multiplier = EXCLUDED.slow_multiplier,
                unsure_multiplier = EXCLUDED.unsure_multiplier,
                festival_week_multiplier = EXCLUDED.festival_week_multiplier,
                festival_day_multiplier = EXCLUDED.festival_day_multiplier,
                snowstorm_multiplier = EXCLUDED.snowstorm_multiplier,
                target_waste_min_pct = EXCLUDED.target_waste_min_pct,
                target_waste_max_pct = EXCLUDED.target_waste_max_pct,
                auto_calendar_events_enabled = EXCLUDED.auto_calendar_events_enabled,
                notify_in_app = EXCLUDED.notify_in_app,
                notify_email = EXCLUDED.notify_email,
                notify_forecast_shift = EXCLUDED.notify_forecast_shift,
                forecast_shift_threshold_pct = EXCLUDED.forecast_shift_threshold_pct,
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
                payload["target_waste_min_pct"],
                payload["target_waste_max_pct"],
                payload["auto_calendar_events_enabled"],
                payload["notify_in_app"],
                payload["notify_email"],
                payload["notify_forecast_shift"],
                payload["forecast_shift_threshold_pct"],
            ),
        )

        write_settings_snapshot(cur, store_id, changed_by, payload)
        conn.commit()
        return jsonify({"message": "Settings rolled back", "settings": payload}), 200
    finally:
        return_connection(conn)
