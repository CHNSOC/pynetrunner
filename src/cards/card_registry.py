import json

from base import Card
class CardRegistry:
    def __init__(self):
        self.cards = {}

    def load_cards_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            card_data = json.load(file)
            print(f"Loaded {len(card_data['data'])} cards from {file_path}")
            for card_info in card_data["data"]:
                card = Card(card_info)
                self.cards[card.id] = card

    def get_card(self, card_id):
        return self.cards.get(card_id)

    def get_all_cards(self):
        return list(self.cards.values())
