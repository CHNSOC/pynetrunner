from random import shuffle
from typing import List, Optional

from src.cards.base import Card


class Deck:
    def __init__(self, cards: List[Card]):
        self.cards = cards
        shuffle(self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None

    def add_card(self, card: Card):
        self.cards.append(card)
