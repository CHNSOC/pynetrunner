import json
from typing import Dict, Any, Callable

from cards.base import Card

class CardRegistry:
    def __init__(self):
        self.cards_data: Dict[str, Dict[str, Any]] = {}
        self.card_factories: Dict[str, Callable[[], Card]] = {}

    def load_card_data(self, json_file_path: str):
        with open(json_file_path, 'r') as file:
            self.cards_data = json.load(file)

    def register_card_factory(self, card_id: str, factory: Callable[[], Card]):
        self.card_factories[card_id] = factory

    def create_card(self, card_id: str) -> Card:
        if card_id not in self.card_factories:
            raise ValueError(f"No factory registered for card ID: {card_id}")
        
        card_data = self.cards_data.get(card_id)
        if not card_data:
            raise ValueError(f"No data found for card ID: {card_id}")

        card = self.card_factories[card_id]()
        card.apply_data(card_data)
        return card