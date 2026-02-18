from __future__ import annotations

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, condecimal, confloat, conint

DecisionLiteral = Literal["GRADE", "SELL", "HOLD", "BUY", "PASS"]
RiskLiteral = Literal["Low", "Medium", "High"]

class CardIdentifyRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)

class CardIdentity(BaseModel):
    card_key: str
    display_name: str
    category: Literal["sports", "tcg"] = "tcg"
    year: Optional[int] = None
    set_name: Optional[str] = None
    card_number: Optional[str] = None
    variant: Optional[str] = None

class CompsRequest(BaseModel):
    identity: CardIdentity

class SoldComp(BaseModel):
    sold_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    sold_date_utc: str
    title: str

class MarketStats(BaseModel):
    p25: condecimal(gt=0, max_digits=10, decimal_places=2)
    median: condecimal(gt=0, max_digits=10, decimal_places=2)
    p75: condecimal(gt=0, max_digits=10, decimal_places=2)
    comps_count: conint(ge=0)
    spread_ratio: confloat(ge=0)
    confidence: conint(ge=0, le=100)
    currency: str = "USD"

class CompsResponse(BaseModel):
    identity: CardIdentity
    comps: List[SoldComp]
    stats: MarketStats

class ConditionMetrics(BaseModel):
    centering: confloat(ge=0, le=10)
    corners: confloat(ge=0, le=10)
    edges: confloat(ge=0, le=10)
    surface: confloat(ge=0, le=10)
    issue_flag: bool = False

class DecisionRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    listed_price: Optional[condecimal(gt=0, max_digits=10, decimal_places=2)] = None
    metrics: ConditionMetrics

class MarketValueOut(BaseModel):
    p25: condecimal(gt=0, max_digits=10, decimal_places=2)
    median: condecimal(gt=0, max_digits=10, decimal_places=2)
    p75: condecimal(gt=0, max_digits=10, decimal_places=2)
    currency: str = "USD"

class RoiOut(BaseModel):
    expected_net: condecimal(max_digits=10, decimal_places=2)
    roi_pct: confloat()
    breakeven_grade: str

class DecisionResponse(BaseModel):
    decision: DecisionLiteral
    confidence: conint(ge=0, le=100)
    risk: RiskLiteral
    market_value: MarketValueOut
    grade_probabilities: Dict[str, confloat(ge=0, le=1)]
    roi: RoiOut
    explanation: List[str]
