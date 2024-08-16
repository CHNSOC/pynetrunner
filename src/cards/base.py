import textwrap



class Card:

    @staticmethod
    def parse_attribute(attributes: dict, key, default_value, data_type=str):
        value = attributes.get(key, default_value)
        if value is None:
            return default_value
        try:
            return data_type(value)
        except (ValueError, TypeError):
            print(f"Warning: Invalid {key} value '{value}'. Using default: {default_value}")
            return default_value
    def __init__(self, card_data):
        attributes = card_data.get("attributes", {})

        self.id = card_data.get("id")
        self.name = Card.parse_attribute(attributes, "title", "")
        self.type = Card.parse_attribute(attributes, "card_type_id", "")
        self.text = Card.parse_attribute(attributes, "text", "")
        self.cost = Card.parse_attribute(attributes, "cost", 0, int)
        self.faction = Card.parse_attribute(attributes, "faction_id", "")
        self.side = Card.parse_attribute(attributes, "side_id", "")
        self.strength = Card.parse_attribute(attributes, "strength", None)
        self.stripped_text = Card.parse_attribute(attributes, "stripped_text", "")
        self.is_unique = Card.parse_attribute(attributes, "is_unique", False, bool)
        self.subtypes = Card.parse_attribute(attributes, "card_subtype_ids", None, list)
        self.influence_cost = Card.parse_attribute(attributes, "influence_cost", None, int)
        self.base_link = Card.parse_attribute(attributes, "base_link", None, int)
        self.deck_limit = Card.parse_attribute(attributes, "deck_limit", None, int)
        self.influence_limit = Card.parse_attribute(attributes, "influence_limit", "")
        self.agenda_points = Card.parse_attribute(attributes, "agenda_points", None, int)
        self.trash_cost = Card.parse_attribute(attributes, "trash_cost", None, int)
        self.memory_cost = Card.parse_attribute(attributes, "memory_cost", None, int)
        self.date_release = Card.parse_attribute(attributes, "date_release", None)
        self.minimum_deck_size = Card.parse_attribute(
            attributes, "minimum_deck_size", None, int
        )
        self.display_subtypes = Card.parse_attribute(attributes, "display_subtypes", "")
        self.advancement_requirement = Card.parse_attribute(
            attributes, "advancement_requirement", 0, int
        )

        self.advancement_tokens = 0
        self.location = None

        self.effects = {}

    def to_string(self):
        attributes = [
            f"ID: {self.id}",
            f"Name: {self.name}",
            f"Type: {self.type}",
            f"Text: {self.text}",
            f"Cost: {self.cost}",
            f"Faction: {self.faction}",
            f"Side: {self.side}",
            f"Strength: {self.strength}",
            f"Stripped Text: {self.stripped_text}",
            f"Is Unique: {self.is_unique}",
            f"Subtypes: {', '.join(self.subtypes)}",
            f"Influence Cost: {self.influence_cost}",
            f"Base Link: {self.base_link}",
            f"Deck Limit: {self.deck_limit}",
            f"Influence Limit: {self.influence_limit}",
            f"Advancement Requirement: {self.advancement_requirement}",
            f"Agenda Points: {self.agenda_points}",
            f"Trash Cost: {self.trash_cost}",
            f"Memory Cost: {self.memory_cost}",
            f"Date Release: {self.date_release}",
            f"Minimum Deck Size: {self.minimum_deck_size}",
            f"Display Subtypes: {self.display_subtypes}",
            f"  Additional Cost: {self.additional_cost}",
            f"  Advanceable: {self.advanceable}",
            f"  Gains Subroutines: {self.gains_subroutines}",
            f"  Interrupt: {self.interrupt}",
            f"  Link Provided: {self.link_provided}",
            f"  MU Provided: {self.mu_provided}",
            f"  Number of Printed Subroutines: {self.num_printed_subroutines}",
            f"  On Encounter Effect: {self.on_encounter_effect}",
            f"  Performs Trace: {self.performs_trace}",
            f"  Recurring Credits Provided: {self.recurring_credits_provided}",
            f"  Rez Effect: {self.rez_effect}",
            f"  Trash Ability: {self.trash_ability}",
        ]
        return "\n".join(attributes)

    @staticmethod
    def format_text(text, width=60, indent=4):
        return textwrap.fill(
            text,
            width=width,
            initial_indent=" " * indent,
            subsequent_indent=" " * indent,
        )

    def pretty_print(self):
        border = "+" + "-" * 68 + "+"
        separator = "|" + "-" * 68 + "|"

        print(border)
        print(f"| {self.name:<66} |")
        print(separator)

        # Common attributes for all card types
        print(f"| Type: {self.type:<60} |")
        print(f"| Faction: {self.faction:<57} |")
        print(f"| Side: {self.side:<60} |")
        if self.subtypes:
            subtypes = ", ".join(self.subtypes)
            print(f"| Subtypes: {subtypes:<56} |")

        if self.cost is not None:
            print(f"| Cost: {self.cost:<60} |")

        if self.influence_cost:
            print(f"| Influence: {self.influence_cost:<55} |")

        print(separator)

        # Card text
        if self.text:
            print("| Text: " + " " * 61 + "|")
            for line in self.format_text(self.text).split("\n"):
                print(f"| {line:<66} |")
            print(separator)

        # Type-specific attributes
        if self.type == "ice":
            print(f"| Strength: {self.strength:<56} |")
            if self.num_printed_subroutines:
                print(f"| Subroutines: {self.num_printed_subroutines:<52} |")
        elif self.type == "agenda":
            print(f"| Advancement Requirement: {self.advancement_requirement:<41} |")
            print(f"| Agenda Points: {self.agenda_points:<51} |")
        elif self.type in ["asset", "upgrade"]:
            print(f"| Trash Cost: {self.trash_cost:<54} |")
        elif self.type == "program":
            if self.memory_cost:
                print(f"| Memory Units: {self.memory_cost:<52} |")
            if self.strength:
                print(f"| Strength: {self.strength:<56} |")
        elif self.type == "Hardware":
            if self.base_link:
                print(f"| Base Link: {self.base_link:<54} |")

        # Additional attributes
        if self.is_unique:
            print(
                "| ◆ Unique                                                            |"
            )

        print(border)

    def play(self, player, game):
        if player.credits >= self.cost:
            player.credits -= self.cost
            player.clicks -= 1
            game.effect_manager.handle_on_play(self, player)
            return True
        return False

    def use_click_ability(self, player, game):
        game.effect_manager.handle_click_ability(self, player)

    def use_paid_ability(self, player, game, ability_index):
        game.effect_manager.handle_paid_ability(self, player, ability_index)

    def rez(self, player):
        if not self.is_rezzed:
            self.is_rezzed = True
            return True
        return False

    def derez(self):
        if self.type in ["ice", "asset", "upgrade"]:
            self.is_rezzed = False

    def advance(self):
        if self.type == "agenda" or (self.type == "asset" and self.can_be_advanced):
            self.advancement_tokens += 1

    def add_virus_counter(self):
        self.virus_counters += 1

    def remove_virus_counter(self):
        if self.virus_counters > 0:
            self.virus_counters -= 1

    def can_be_advanced(self):
        return self.type in ["agenda", "asset"] and hasattr(
            self, "advancement_requirement"
        )

    def can_be_scored(self):
        return (
            self.type == "agenda"
            and self.advancement_tokens >= self.advancement_requirement
        )

    def apply_data(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.cost = data.get("cost")
        self.type = data.get("type")
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def add_event_listener(self, event, callback):
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(callback)

    def trigger(self, event, *args):
        for listener in self.event_listeners.get(event, []):
            listener(*args)

    def get_effect(self):
        # This method should be overridden in subclasses
        return lambda player, game: None
