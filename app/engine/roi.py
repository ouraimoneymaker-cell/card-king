from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple

def q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def expected_value_from_probs(base_market_median: Decimal, probs: Dict[str, float], grade_multipliers: Dict[str, float]) -> Decimal:
    ev = Decimal("0")
    for grade, p in probs.items():
        mult = Decimal(str(grade_multipliers.get(grade, 1.0)))
        ev += Decimal(str(p)) * (base_market_median * mult)
    return ev

def roi_summary(
    market_median: Decimal,
    probs: Dict[str, float],
    grade_multipliers: Dict[str, float],
    grading_fee: Decimal,
    shipping_insurance: Decimal,
    platform_fee_pct: Decimal,
    risk_discount_pct: Decimal,
) -> Tuple[Decimal, float, str]:
    expected_sale = expected_value_from_probs(market_median, probs, grade_multipliers)

    platform_fee = expected_sale * platform_fee_pct
    risk_discount = expected_sale * risk_discount_pct

    expected_net = expected_sale - platform_fee - grading_fee - shipping_insurance - risk_discount

    denom = grading_fee + shipping_insurance
    roi_pct = float(expected_net / denom) * 100.0 if denom > 0 else 0.0

    ordered = ["PSA10", "PSA9", "PSA8", "PSA7", "LT7"]
    breakeven = "LT7"
    for g in ordered:
        mult = Decimal(str(grade_multipliers.get(g, 1.0)))
        sale = market_median * mult
        net = sale - (sale * platform_fee_pct) - grading_fee - shipping_insurance - (sale * risk_discount_pct)
        if net >= 0:
            breakeven = g
            break

    return q2(expected_net), roi_pct, breakeven
