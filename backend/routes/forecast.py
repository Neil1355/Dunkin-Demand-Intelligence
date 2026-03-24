from flask import Blueprint, request, jsonify
from models.db import get_connection, return_connection
from datetime import date, timedelta

forecast_bp = Blueprint("forecast", __name__)


def clamp_multiplier(value: float) -> float:
    return max(0.5, min(2.0, value))


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    first_day = date(year, month, 1)
    offset = (weekday - first_day.weekday() + 7) % 7
    return first_day + timedelta(days=offset + (n - 1) * 7)


def get_calendar_multiplier(target_date: date) -> float:
    # Heuristic holiday/festival windows commonly affecting foot traffic.
    fixed_windows = [
        (date(target_date.year, 12, 25), 5, 1.15),  # Christmas week
        (date(target_date.year, 1, 1), 3, 1.08),    # New Year window
        (date(target_date.year, 7, 4), 3, 1.10),    # July 4th window
        (date(target_date.year, 10, 31), 2, 1.06),  # Halloween
        (date(target_date.year, 2, 14), 2, 1.05),   # Valentine's day
    ]

    for event_date, radius_days, factor in fixed_windows:
        if abs((target_date - event_date).days) <= radius_days:
            return factor

    # Thanksgiving week (US): 4th Thursday of November, apply uplift week-wide.
    thanksgiving = nth_weekday_of_month(target_date.year, 11, 3, 4)  # Thursday=3
    week_start = thanksgiving - timedelta(days=4)
    week_end = thanksgiving + timedelta(days=2)
    if week_start <= target_date <= week_end:
        return 1.12

    return 1.0


def get_expectation_multiplier(expectation: str | None) -> float:
    if not expectation:
        return 1.0
    normalized = expectation.strip().lower()
    mapping = {
        "yes": 1.18,
        "busy": 1.18,
        "maybe": 1.07,
        "not_sure": 1.00,
        "unsure": 1.00,
        "normal": 1.00,
        "no": 0.86,
        "slow": 0.86,
        "slower": 0.86,
    }
    return mapping.get(normalized, 1.0)


def get_reason_multiplier(reason: str | None) -> float:
    if not reason:
        return 1.0
    normalized = reason.strip().lower()
    mapping = {
        # Busy reasons
        "festival_week": 1.20,
        "festival_day": 1.14,
        "local_event": 1.10,
        "school_day": 1.06,
        "good_weather": 1.04,
        "promotion_day": 1.08,
        "pay_cycle": 1.04,

        # Slow reasons
        "snowstorm": 0.72,
        "heavy_rain": 0.88,
        "extreme_cold": 0.84,
        "school_break": 0.92,
        "road_closure": 0.85,

        # Uncertain/neutral
        "mixed_signals": 1.00,
        "uncertain_weather": 0.98,
        "partial_event": 1.02,
        "new_pattern": 1.00,
        "manager_override": 1.00,
    }
    return mapping.get(normalized, 1.0)

@forecast_bp.get("/next-day")
def next_day_forecast():
    store_id = request.args.get("store_id", type=int)
    if not store_id:
        return jsonify({"error": "store_id required"}), 400

    # Optional direct override; if not provided, use context + calendar heuristics.
    adjustment_override = request.args.get("adjustment", type=float)

    conn = get_connection()
    try:
        cur = conn.cursor()

        target_date = request.args.get("target_date", type=lambda d: date.fromisoformat(d)) or (date.today() + timedelta(days=1))
        target_isodow = target_date.isoweekday()

        context_multiplier = 1.0
        calendar_multiplier = get_calendar_multiplier(target_date)
        saved_expectation = None
        saved_reason = None

        cur.execute(
            """
            SELECT expectation, reason
            FROM public.forecast_context
            WHERE store_id = %s AND target_date = %s
            LIMIT 1
            """,
            (store_id, target_date),
        )
        context_row = cur.fetchone()

        if context_row:
            saved_expectation = context_row.get("expectation")
            saved_reason = context_row.get("reason")
            context_multiplier *= get_expectation_multiplier(saved_expectation)
            context_multiplier *= get_reason_multiplier(saved_reason)

        computed_multiplier = clamp_multiplier(context_multiplier * calendar_multiplier)
        final_multiplier = clamp_multiplier(adjustment_override) if adjustment_override is not None else computed_multiplier

        cur.execute("SELECT product_id FROM products WHERE is_active = TRUE")
        products = cur.fetchall()

        forecast = {}

        for product in products:
            product_id = product["product_id"]

            # Use recent same-weekday performance from imported throwaway sheets.
            # sold ~= produced - waste.
            cur.execute("""
                SELECT
                    GREATEST(COALESCE(dt.produced, 0) - COALESCE(dt.waste, 0), 0) AS sold
                FROM daily_throwaway dt
                WHERE dt.store_id = %s
                  AND dt.product_id = %s
                  AND dt.date < %s
                  AND EXTRACT(ISODOW FROM dt.date) = %s
                ORDER BY dt.date DESC
                LIMIT 4
            """, (store_id, product_id, target_date, target_isodow))

            rows = cur.fetchall()
            # Fallback: if no same-weekday history exists yet, use most recent rows.
            if not rows:
                cur.execute("""
                    SELECT
                        GREATEST(COALESCE(dt.produced, 0) - COALESCE(dt.waste, 0), 0) AS sold
                    FROM daily_throwaway dt
                    WHERE dt.store_id = %s
                      AND dt.product_id = %s
                      AND dt.date <= %s
                    ORDER BY dt.date DESC
                    LIMIT 4
                """, (store_id, product_id, target_date))
                rows = cur.fetchall()

            if not rows:
                continue

            sold_values = [int(r["sold"] or 0) for r in rows]
            avg_sold = max(int(round(sum(sold_values) / len(sold_values))), 0)
            
            # Apply final multiplier based on context + seasonal calendar heuristics.
            adjusted_quantity = max(int(round(avg_sold * final_multiplier)), 0)

            cur.execute("""
                INSERT INTO forecast_history
                (store_id, product_id, forecast_date, target_date, predicted_quantity, model_version, status)
                VALUES (%s, %s, CURRENT_DATE, %s, %s, 'v1', 'pending')
                ON CONFLICT (store_id, product_id, target_date)
                DO UPDATE SET
                    forecast_date = EXCLUDED.forecast_date,
                    predicted_quantity = EXCLUDED.predicted_quantity,
                    model_version = EXCLUDED.model_version,
                    status = EXCLUDED.status,
                    created_at = NOW();
            """, (store_id, product_id, target_date, adjusted_quantity))

            forecast[product_id] = adjusted_quantity

        conn.commit()
        cur.close()

        return jsonify({
            "store_id": store_id,
            "target_date": str(target_date),
            "forecast": forecast,
            "generated_products": len(forecast),
            "applied_multiplier": final_multiplier,
            "context_multiplier": context_multiplier,
            "calendar_multiplier": calendar_multiplier,
            "context_expectation": saved_expectation,
            "context_reason": saved_reason,
        })
    finally:
        return_connection(conn)
