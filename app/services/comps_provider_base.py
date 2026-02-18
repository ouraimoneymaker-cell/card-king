from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple
from app.engine.schemas import CardIdentity, SoldComp, MarketStats

class CompsProvider(ABC):
    @abstractmethod
    def get_recent_sold_comps(self, identity: CardIdentity) -> Tuple[List[SoldComp], MarketStats]:
        raise NotImplementedError
