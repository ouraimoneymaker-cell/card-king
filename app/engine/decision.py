from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from app.engine.market import spread_ratio as calc_spread_ratio, comps_confidence
from app.engine.roi import roi_summary

Decision = str

@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    confidence: int
    risk: str
    explanation: List[str]
    expected_net: Decimal
    roi_pct: float
    breakeven_grade: str

def _clamp_int(x: float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(round(x))))

def decide(
    market_p25: Decimal,
    market_median: Decimal,
    market_p75: Decimal,
    comps_count: int,
    grade_probs: Dict[str, float],
    fees: Dict,
    listed_price: Optional[Decimal] = None,
    risk_tolerance: str = "standard",
) -> DecisionResult:
    thresholds = fees["decision_thresholds"]
    grading_fee = Decimal(str(fees["grading"]["grading_fee"]))
    shipping_ins = Decimal(str(fees["grading"]["shipping_insurance"]))
    platform_fee_pct = Decimal(str(fees["platform"]["platform_fee_pct"]))
    risk_discount_pct = Decimal(str(fees["risk"]["risk_discount_pct"]))
    grade_multipliers = fees["grade_multipliers"]

    spread = calc_spread_ratio(market_p25, market_p75, market_median)
    market_conf = comps_confidence(comps_count, spread)

    psa9_plus = float(grade_probs.get("PSA10", 0.0) + grade_probs.get("PSA9", 0.0))

    expected_net, roi_pct, breakeven = roi_summary(
        market_median=market_median,
        probs=grade_probs,
        grade_multipliers=grade_multipliers,
        grading_fee=grading_fee,
        shipping_insurance=shipping_ins,
        platform_fee_pct=platform_fee_pct,
        risk_discount_pct=risk_discount_pct,
    )

    explanation: List[str] = []
    explanation.append(f"Comps: {comps_count} recent sales; market confidence {market_conf}/100.")
    explanation.append(f"Market range: ${market_p25}–${market_p75} (median ${market_median}).")
    explanation.append(f"PSA 9+ probability: {psa9_plus:.0%}.")
    explanation.append(f"Expected net after fees: ${expected_net}.")

    risk = "High"
    if comps_count >= thresholds["min_comps_count"] and spread <= thresholds["max_price_spread_ratio_for_low_risk"]:
        risk = "Low"
    elif comps_count >= max(3, thresholds["min_comps_count"] // 2):
        risk = "Medium"

    if comps_count < max(3, thresholds["min_comps_count"] // 2):
        decision = "PASS"
        explanation.insert(0, "Not enough reliable comps to make a confident call.")
        conf = _clamp_int(market_conf * 0.6, 0, 100)
        return DecisionResult(decision, conf, "High", explanation[:4], expected_net, roi_pct, breakeven)

    if listed_price is not None:
        undervalue_margin = Decimal(str(thresholds["buy_undervalue_margin"]))
        if listed_price <= (market_p25 * (Decimal("1") - undervalue_margin)) and risk != "High":
            decision = "BUY"
            conf = _clamp_int(0.5 * market_conf + 40, 0, 100)
            explanation.insert(0, "Listed price is significantly below low-end comps.")
            return DecisionResult(decision, conf, risk, explanation[:4], expected_net, roi_pct, breakeven)

    min_profit = Decimal(str(thresholds["min_expected_net_profit"]))
    min_psa9p = float(thresholds["min_psa9_plus_prob"])

    if expected_net >= min_profit and psa9_plus >= min_psa9p and risk != "High":
        decision = "GRADE"
        conf = _clamp_int(0.6 * market_conf + 40 * psa9_plus, 0, 100)
        explanation.insert(0, "High upside after grading fees with strong PSA 9+ odds.")
        return DecisionResult(decision, conf, risk, explanation[:4], expected_net, roi_pct, breakeven)

    if expected_net < 0 and market_conf >= 55:
        decision = "SELL"
        conf = _clamp_int(0.7 * market_conf + 20, 0, 100)
        explanation.insert(0, "Grading math is unfavorable; selling raw is safer.")
        return DecisionResult(decision, conf, risk, explanation[:4], expected_net, roi_pct, breakeven)

    decision = "HOLD" if market_conf < 75 else "SELL"
    conf = _clamp_int(0.65 * market_conf + 10, 0, 100)
    explanation.insert(0, "Signals are mixed; avoid forcing a risky move.")
    return DecisionResult(decision, conf, risk, explanation[:4], expected_net, roi_pct, breakeven)
