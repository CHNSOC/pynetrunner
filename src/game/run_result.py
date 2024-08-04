from dataclasses import dataclass
from typing import List
from ..cards.base import Card

@dataclass
class RunResult:
    successful: bool
    accessed_cards: List[Card]
    message: str