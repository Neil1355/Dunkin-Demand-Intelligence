def forecast_quantity(rows):
    total_produced = sum(r["quantity_produced"] for r in rows)
    total_waste = sum(r["waste"] for r in rows)

    if total_produced == 0:
        return 0

    avg = total_produced / len(rows)
    waste_ratio = total_waste / total_produced

    if waste_ratio > 0.20:
        return int(avg * 0.9)
    elif waste_ratio < 0.05:
        return int(avg * 1.05)
    else:
        return int(avg)
