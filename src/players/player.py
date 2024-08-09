
import random
from typing import Dict, List, Optional
from random import shuffle
from typing import List, Optional

from ..cards.base import Card


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


class Player:
    def __init__(self, deck: Deck, identity: Optional[Card] = None):
        self.name = identity.name if identity else "Anonymous"
        self.deck = deck
        self.identity: Optional[Card] = None
        self.hand: List[Card] = []
        self.credits = 5
        self.clicks = 0
        self.has_mulliganed = False
        self.score_area: List[Card] = []
        self.installed_cards = []

    def __str__(self):
        return f"{self.name} - Credits: {self.credits}, Clicks: {self.clicks}, Hand size: {len(self.hand)}"

    def draw(self, count: int = 1):
        for _ in range(count):
            if self.deck:
                self.hand.append(self.deck.draw())
            else:
                # Handle deck out situation
                pass

    def mulligan(self):
        if not self.has_mulliganed:
            # Return all cards to the deck
            self.deck.cards.extend(self.hand)
            self.hand.clear()
            # Shuffle the deck
            random.shuffle(self.deck.cards)
            # Draw a new hand
            self.draw(5)
            self.has_mulliganed = True
        else:
            print(f"{self.name} has already mulliganed in this game.")

    def set_identity(self, identity_card):
        self.identity = identity_card

    def gain_credits(self, amount: int):
        self.credits += amount

    def spend_credits(self, amount: int):
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False

    def discard_down_to_max_hand_size(self):
        while len(self.hand) > self.get_max_hand_size():
            max_hand_size = self.get_max_hand_size()
            card_index = int(input(f"You have {len(self.hand)} cards. Discard down to { max_hand_size}. Choose a card to discard: ")) - 1
            discarded_card = self.hand.pop(card_index)
            print(f"Discarded: {discarded_card.name}")

    def get_max_hand_size(self) -> int:
        # Implement logic to calculate max hand size, including card effects
        return 5
