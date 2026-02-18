from decimal import Decimal
from app.engine.roi import roi_summary

def test_roi_summary_deterministic():
    probs = {"PSA10":0.1,"PSA9":0.4,"PSA8":0.3,"PSA7":0.1,"LT7":0.1}
    multipliers = {"PSA10":2.0,"PSA9":1.35,"PSA8":1.1,"PSA7":0.95,"LT7":0.8}
    expected_net, roi_pct, breakeven = roi_summary(
        market_median=Decimal("100"),
        probs=probs,
        grade_multipliers=multipliers,
        grading_fee=Decimal("19"),
        shipping_insurance=Decimal("18"),
        platform_fee_pct=Decimal("0.1325"),
        risk_discount_pct=Decimal("0.05"),
    )
    assert expected_net.quantize(Decimal("0.01")) == expected_net
    assert isinstance(roi_pct, float)
    assert breakeven in ["PSA10","PSA9","PSA8","PSA7","LT7"]
