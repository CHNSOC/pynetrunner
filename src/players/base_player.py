import random
from ..cards.deck import Deck
from ..cards.base import Card
from typing import List, Optional

from src.common.stat_modifier import StatModifier, TemporaryModifier


class Player:
    def __init__(self, deck: Deck, identity: Optional[Card] = None):
        self.name = identity.name if identity else "Anonymous"
        self.deck = deck
        self.identity = identity
        self.hand: List[Card] = []
        self.credits = 5
        self.clicks = 0
        self.has_mulliganed = False
        self.score_area: List[Card] = []
        self.installed_cards = []
        self.stat_modifiers = []

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

    def get_max_hand_size(self) -> int:
        # Implement logic to calculate max hand size, including card effects
        return 5

    def get_active_effects(self, phase):
        active_effects = []
        for card in self.get_all_installed_cards():
            if phase in card.effects:
                active_effects.append((card, card.effects[phase]))
        return active_effects

    def add_modifier(self, source, stat, amount):
        self.stat_modifiers.append(StatModifier(source, stat, amount))

    def remove_modifiers(self, source):
        self.stat_modifiers = [
            mod for mod in self.stat_modifiers if mod.source != source
        ]

    def add_temporary_modifier(self, source, stat, amount, duration):
        self.stat_modifiers.append(TemporaryModifier(source, stat, amount, duration))

    def update_modifiers(self):
        for mod in self.stat_modifiers:
            if isinstance(mod, TemporaryModifier):
                mod.duration -= 1
        self.stat_modifiers = [
            mod
            for mod in self.stat_modifiers
            if not isinstance(mod, TemporaryModifier) or mod.duration > 0
        ]

    def search_deck(self, card_name):
        for card in self.deck.cards:
            if card.name == card_name:
                return card
        return None

    def shuffle_deck(self):
        random.shuffle(self.deck.cards)

    def can_pay(self, cost):
        return self.credits >= cost

    def score_agenda(self, agenda: Card):
        # TODO: Move card from server to score area, triggering any on-score effects
        self.score_area.append(agenda)
        print(f"Scored agenda: {agenda.name} worth {agenda.agenda_points} points.")
