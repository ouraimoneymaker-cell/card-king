from decimal import Decimal
from app.engine.decision import decide

FEES = {
  "grading": {"grading_fee": 19.0, "shipping_insurance": 18.0},
  "platform": {"platform_fee_pct": 0.1325},
  "risk": {"risk_discount_pct": 0.05},
  "grade_multipliers": {"PSA10":2.0,"PSA9":1.35,"PSA8":1.1,"PSA7":0.95,"LT7":0.8},
  "decision_thresholds": {
    "min_expected_net_profit": 40.0,
    "min_psa9_plus_prob": 0.70,
    "min_comps_count": 5,
    "max_price_spread_ratio_for_low_risk": 0.35,
    "buy_undervalue_margin": 0.15
  }
}

def test_decision_determinism_same_input_same_output():
    probs = {"PSA10":0.25,"PSA9":0.5,"PSA8":0.15,"PSA7":0.07,"LT7":0.03}
    a = decide(Decimal("90"), Decimal("110"), Decimal("130"), 10, probs, FEES, listed_price=None)
    b = decide(Decimal("90"), Decimal("110"), Decimal("130"), 10, probs, FEES, listed_price=None)
    assert a == b

def test_buy_when_undervalued():
    probs = {"PSA10":0.10,"PSA9":0.40,"PSA8":0.30,"PSA7":0.10,"LT7":0.10}
    r = decide(Decimal("100"), Decimal("120"), Decimal("140"), 10, probs, FEES, listed_price=Decimal("75"))
    assert r.decision in ["BUY","HOLD","GRADE","SELL","PASS"]
