from decimal import Decimal
from app.engine.market import percentile, median, trimmed_mean, spread_ratio, comps_confidence

def test_percentiles_basic():
    vals = [Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40")]
    assert percentile(vals, 25) == Decimal("17.5")
    assert percentile(vals, 50) == Decimal("25")
    assert percentile(vals, 75) == Decimal("32.5")

def test_median_even():
    vals = [Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40")]
    assert median(vals) == Decimal("25")

def test_trimmed_mean():
    vals = [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("100")]
    tm = trimmed_mean(vals, 0.25)  # drops 1 and 100
    assert tm == Decimal("2.5")

def test_spread_ratio_and_confidence():
    p25 = Decimal("80")
    p75 = Decimal("120")
    med = Decimal("100")
    spr = spread_ratio(p25, p75, med)
    conf = comps_confidence(8, spr)
    assert spr == 0.4
    assert 0 <= conf <= 100
