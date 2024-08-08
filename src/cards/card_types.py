# card_types.py

from .base import Card

class ICE(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.strength = card_data['attributes'].get('strength', 0)
        self.subroutines = self.parse_subroutines(card_data['attributes'].get('text', ''))

    def parse_subroutines(self, text):
        return [line.strip() for line in text.split('\n') if line.strip().startswith('‣')]

class Agenda(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.advancement_requirement = card_data['attributes'].get('advancement_requirement', 0)
        self.agenda_points = card_data['attributes'].get('agenda_points', 0)

class Operation(Card):
    def __init__(self, card_data):
        super().__init__(card_data)

class Program(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.strength = card_data['attributes'].get('strength', 0)
        self.memory_cost = card_data['attributes'].get('memory_cost', 1)

class Event(Card):
    def __init__(self, card_data):
        super().__init__(card_data)

class Hardware(Card):
    def __init__(self, card_data):
        super().__init__(card_data)

class Resource(Card):
    def __init__(self, card_data):
        super().__init__(card_data)

class Asset(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.trash_cost = card_data['attributes'].get('trash_cost', 0)

class Upgrade(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.trash_cost = card_data['attributes'].get('trash_cost', 0)