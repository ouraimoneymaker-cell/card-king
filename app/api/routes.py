from __future__ import annotations

import json
import hashlib
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter

from app.engine.schemas import (
    CardIdentifyRequest,
    CardIdentity,
    CompsRequest,
    CompsResponse,
    DecisionRequest,
    DecisionResponse,
    MarketValueOut,
    RoiOut,
)
from app.services.comps_provider_stub import StubCompsProvider
from app.engine.grading import grade_probabilities
from app.engine.decision import decide
from app.data.db import get_conn
import os

router = APIRouter(prefix="/api", tags=["api"])

_FEES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "fees_default.json")

def _load_fees() -> Dict[str, Any]:
    with open(os.path.abspath(_FEES_PATH), "r", encoding="utf-8") as f:
        return json.load(f)

def _stable_card_key(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()[:16]

@router.post("/identify", response_model=CardIdentity)
def identify(req: CardIdentifyRequest) -> CardIdentity:
    q = req.query.strip()
    key = _stable_card_key(q)
    # DEFAULT: deterministic stub identity parsing
    category = "tcg"
    if any(tok in q.lower() for tok in ["psa", "topps", "panini", "rookie", "nba", "nfl", "mlb"]):
        category = "sports"

    display = q if len(q) <= 80 else q[:77] + "..."
    return CardIdentity(card_key=key, display_name=display, category=category)

@router.post("/comps", response_model=CompsResponse)
def comps(req: CompsRequest) -> CompsResponse:
    provider = StubCompsProvider()
    comps_list, stats = provider.get_recent_sold_comps(req.identity)

    # cache (DEFAULT ttl handled by caller; cache writes always)
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO comps_cache(card_key, fetched_at_utc, comps_json, stats_json) VALUES(?,?,?,?)",
        (
            req.identity.card_key,
            datetime.now(timezone.utc).isoformat(),
            json.dumps([c.model_dump() for c in comps_list], default=str),
            json.dumps(stats.model_dump(), default=str),
        ),
    )
    conn.commit()
    conn.close()

    return CompsResponse(identity=req.identity, comps=comps_list, stats=stats)

@router.post("/decision", response_model=DecisionResponse)
def decision(req: DecisionRequest) -> DecisionResponse:
    fees = _load_fees()

    identity = identify(CardIdentifyRequest(query=req.query))
    provider = StubCompsProvider()
    comps_list, stats = provider.get_recent_sold_comps(identity)

    probs = grade_probabilities(
        centering=float(req.metrics.centering),
        corners=float(req.metrics.corners),
        edges=float(req.metrics.edges),
        surface=float(req.metrics.surface),
        issue_flag=bool(req.metrics.issue_flag),
    )

    listed_price = Decimal(str(req.listed_price)) if req.listed_price is not None else None

    res = decide(
        market_p25=Decimal(str(stats.p25)),
        market_median=Decimal(str(stats.median)),
        market_p75=Decimal(str(stats.p75)),
        comps_count=int(stats.comps_count),
        grade_probs=probs,
        fees=fees,
        listed_price=listed_price,
        risk_tolerance="standard",
    )

    resp = DecisionResponse(
        decision=res.decision,  # type: ignore
        confidence=int(res.confidence),
        risk=res.risk,  # type: ignore
        market_value=MarketValueOut(p25=stats.p25, median=stats.median, p75=stats.p75, currency=stats.currency),
        grade_probabilities=probs,
        roi=RoiOut(expected_net=res.expected_net, roi_pct=res.roi_pct, breakeven_grade=res.breakeven_grade),
        explanation=res.explanation,
    )

    # log decision
    conn = get_conn()
    conn.execute(
        "INSERT INTO decision_log(created_at_utc, request_json, response_json) VALUES(?,?,?)",
        (
            datetime.now(timezone.utc).isoformat(),
            json.dumps(req.model_dump(), default=str),
            json.dumps(resp.model_dump(), default=str),
        ),
    )
    conn.commit()
    conn.close()

    return resp
