import json
from .base import Card
from .card_types import ICE, Agenda, Operation, Program, Event, Hardware, Resource, Asset, Upgrade


class CardRegistry:
    def __init__(self):
        self.cards = {}
        self.effects = {}

    def load_cards_from_json(self, cards_path, effects_path):
        with open(cards_path, 'r', encoding='utf-8') as file:
            card_data = json.load(file)
            for card_info in card_data["data"]:
                card = self.create_card(card_info)
                self.cards[card.id] = card

        with open(effects_path, 'r', encoding='utf-8') as file:
            effects_data = json.load(file)
            for card_id, effect_info in effects_data.items():
                if card_id in self.cards:
                    self.cards[card_id].effects = effect_info.get(
                        'effects', {})

    def create_card(self, card_info):
        card_type = card_info['attributes']['card_type_id']
        card_classes = {
            'agenda': Agenda,
            'ice': ICE,
            'operation': Operation,
            'program': Program,
            'event': Event,
            'hardware': Hardware,
            'resource': Resource,
            'asset': Asset,
            'upgrade': Upgrade
        }
        return card_classes.get(card_type, Card)(card_info)

    def get_card(self, card_id):
        return self.cards.get(card_id)

    def get_all_cards(self):
        return list(self.cards.values())
