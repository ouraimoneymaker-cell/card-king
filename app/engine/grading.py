from __future__ import annotations

from typing import Dict
from math import exp

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _normalize(d: Dict[str, float]) -> Dict[str, float]:
    s = sum(d.values())
    if s <= 0:
        n = len(d)
        return {k: 1.0 / n for k in d}
    return {k: v / s for k, v in d.items()}

def grade_probabilities(centering: float, corners: float, edges: float, surface: float, issue_flag: bool=False) -> Dict[str, float]:
    # Simple deterministic model:
    # average score drives grade; weakest subscore caps.
    avg = (centering + corners + edges + surface) / 4.0
    weakest = min(centering, corners, edges, surface)

    issue_penalty = 0.6 if issue_flag else 1.0

    def bump(x: float, mu: float, sigma: float) -> float:
        return exp(-((x - mu) ** 2) / (2 * sigma ** 2))

    cap10 = _clamp01((weakest - 8.5) / 1.5)
    cap9 = _clamp01((weakest - 7.8) / 2.0)

    raw = {
        "PSA10": bump(avg, 9.85, 0.25) * cap10,
        "PSA9": bump(avg, 9.25, 0.35) * cap9,
        "PSA8": bump(avg, 8.55, 0.40),
        "PSA7": bump(avg, 7.75, 0.45),
        "LT7": bump(avg, 6.80, 0.80),
    }

    raw["PSA10"] *= issue_penalty
    raw["PSA9"] *= issue_penalty
    raw["PSA8"] *= (0.9 + 0.1 * issue_penalty)

    probs = _normalize(raw)
    probs = {k: _clamp01(v) for k, v in probs.items()}
    probs = _normalize(probs)
    return probs
