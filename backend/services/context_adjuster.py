CONTEXT_MULTIPLIERS = {
    "normal": 1.00,
    "busy": 1.15,
    "slow": 0.85,
    "unsure": 1.00
}

def apply_context_adjustment(cur, store_id, target_date):
    # fetch context
    cur.execute("""
        SELECT expectation
        FROM forecast_context
        WHERE store_id = %s
          AND target_date = %s;
    """, (store_id, target_date))

    row = cur.fetchone()
    expectation = row["expectation"] if row else "normal"
    multiplier = CONTEXT_MULTIPLIERS.get(expectation, 1.00)

    # apply adjustment
    cur.execute("""
        UPDATE forecast_history
        SET
          context_expectation = %s,
          context_multiplier = %s,
          adjusted_quantity = ROUND(predicted_quantity * %s)
        WHERE store_id = %s
          AND target_date = %s;
    """, (
        expectation,
        multiplier,
        multiplier,
        store_id,
        target_date
    ))
