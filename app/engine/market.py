from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import List

def quantize_money(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def percentile(values: List[Decimal], p: float) -> Decimal:
    if not values:
        raise ValueError("values empty")
    if p < 0 or p > 100:
        raise ValueError("p must be 0..100")
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    k = (len(vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    d0 = vals[f] * (Decimal(str(c)) - Decimal(str(k)))
    d1 = vals[c] * (Decimal(str(k)) - Decimal(str(f)))
    return (d0 + d1)

def median(values: List[Decimal]) -> Decimal:
    if not values:
        raise ValueError("values empty")
    vals = sorted(values)
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / Decimal("2")

def trimmed_mean(values: List[Decimal], trim_ratio: float = 0.1) -> Decimal:
    if not values:
        raise ValueError("values empty")
    vals = sorted(values)
    n = len(vals)
    k = int(n * trim_ratio)
    core = vals[k:n-k] if n - 2 * k > 0 else vals
    return sum(core) / Decimal(str(len(core)))

def spread_ratio(p25: Decimal, p75: Decimal, med: Decimal) -> float:
    if med <= 0:
        return 0.0
    return float((p75 - p25) / med)

def comps_confidence(count: int, spread_ratio_value: float) -> int:
    # Deterministic heuristic: more comps increases confidence; wider spreads reduce.
    base = min(60, count * 10)  # 0..60
    spread_penalty = int(min(50, max(0.0, spread_ratio_value) * 100))  # 0..50
    conf = max(0, min(100, base + 40 - spread_penalty))
    return int(conf)
