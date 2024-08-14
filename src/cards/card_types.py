# card_types.py

from .base import Card


class ICE(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.strength = card_data["attributes"].get("strength", 0)
        self.subroutines = self.parse_subroutines(
            card_data["attributes"].get("text", "")
        )
        self.num_printed_subroutines = len(self.subroutines)
        

    def parse_subroutines(self, text):
        return [
            line.strip() for line in text.split("\n") if line.strip().startswith("‣")
        ]


class Agenda(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.advancement_requirement = card_data["attributes"].get(
            "advancement_requirement", 0
        )
        self.agenda_points = card_data["attributes"].get("agenda_points", 0)


class Identity(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.minimum_deck_size = card_data["attributes"].get("minimum_deck_size", 45)
        self.influence_limit = card_data["attributes"].get("influence_limit", 15)


class Operation(Card):
    def __init__(self, card_data):
        super().__init__(card_data)


class Program(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.memory_cost = card_data["attributes"].get("memory_cost", 1)
        self.strength = card_data["attributes"].get("strength", 0)

    def can_break(self, ice):
        for ability in self.effects.get("paid_abilities", []):
            if ability["type"] == "break_subroutine" and (
                ability["target"] == "any" or ice.subtype in ability["target"]
            ):
                return True
        return False

    def break_subroutine(self, subroutine, player):
        for ability in self.effects.get("paid_abilities", []):
            if (
                ability["type"] == "break_subroutine"
                and player.credits >= ability["cost"]
            ):
                player.credits -= ability["cost"]
                return True
        return False

    def increase_strength(self, amount, player):
        for ability in self.effects.get("paid_abilities", []):
            if (
                ability["type"] == "increase_strength"
                and player.credits >= ability["cost"]
            ):
                player.credits -= ability["cost"]
                self.strength += amount
                return True
        return False


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
        self.trash_cost = card_data["attributes"].get("trash_cost", 0)


class Upgrade(Card):
    def __init__(self, card_data):
        super().__init__(card_data)
        self.trash_cost = card_data["attributes"].get("trash_cost", 0)
