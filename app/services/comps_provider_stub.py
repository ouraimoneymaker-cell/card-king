from __future__ import annotations

import hashlib
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from random import Random
from typing import List, Tuple

from app.engine.schemas import CardIdentity, SoldComp, MarketStats
from app.engine.market import percentile, median, spread_ratio, comps_confidence, quantize_money

class StubCompsProvider:
    """Deterministic stub comps provider.

    Generates the same comps for the same card_key, every time.
    """

    def get_recent_sold_comps(self, identity: CardIdentity) -> Tuple[List[SoldComp], MarketStats]:
        seed_int = int(hashlib.sha256(identity.card_key.encode("utf-8")).hexdigest()[:16], 16)
        rng = Random(seed_int)

        base = 20.0 if identity.category == "tcg" else 35.0
        base += (seed_int % 7000) / 100.0  # 0..70 shift

        comps: List[SoldComp] = []
        now = datetime.now(timezone.utc)
        for i in range(10):
            noise = rng.uniform(-0.22, 0.28)
            price = max(1.0, base * (1.0 + noise))
            days_ago = int(rng.uniform(1, 45))
            sold_dt = now - timedelta(days=days_ago)
            comps.append(
                SoldComp(
                    sold_price=Decimal(str(round(price, 2))),
                    sold_date_utc=sold_dt.isoformat(),
                    title=f"{identity.display_name} — Sold comp {i+1}",
                )
            )

        values = [Decimal(str(c.sold_price)) for c in comps]
        p25 = quantize_money(percentile(values, 25))
        med = quantize_money(median(values))
        p75 = quantize_money(percentile(values, 75))
        spr = spread_ratio(p25, p75, med)
        conf = comps_confidence(len(values), spr)

        stats = MarketStats(
            p25=p25,
            median=med,
            p75=p75,
            comps_count=len(values),
            spread_ratio=float(spr),
            confidence=conf,
            currency="USD",
        )
        return comps, stats
