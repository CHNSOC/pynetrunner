
import json
from .base import Card
from .card_types import ICE, Agenda, Operation, Program, Event, Hardware, Resource, Asset, Upgrade


class CardRegistry:
    def __init__(self):
        self.cards = {}
        self.effects = {}

    def register_card(self, card_id, card_data):
        self.cards[card_id] = card_data

    def register_effect(self, effect):
        if effect.card_id not in self.effects:
            self.effects[effect.card_id] = []
        self.effects[effect.card_id].append(effect)

    def load_cards_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            card_data = json.load(file)
            print(f"Loaded {len(card_data['data'])} cards from {file_path}")
            for card_info in card_data["data"]:
                card = self.create_card(card_info)
                self.cards[card.id] = card

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

    def get_effects(self, card_id, phase):
        return [effect for effect in self.effects.get(card_id, []) if effect.phase == phase]

    def get_all_cards(self):
        return list(self.cards.values())
