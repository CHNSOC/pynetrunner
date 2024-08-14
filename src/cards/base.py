import textwrap


class Card:
    def __init__(self, card_data):
        attributes = card_data.get("attributes", {})

        self.id = card_data.get("id", "")
        self.name = attributes.get("title", "")
        self.type = attributes.get("card_type_id", "")
        self.text = attributes.get("text", "")
        self.cost = attributes.get("cost")
        self.faction = attributes.get("faction_id", "")
        self.side = attributes.get("side_id", "")
        self.strength = attributes.get("strength")
        self.stripped_text = attributes.get("stripped_text", "")
        self.is_unique = attributes.get("is_unique", False)
        self.subtypes = attributes.get("card_subtype_ids", [])
        self.influence_cost = attributes.get("influence_cost")
        self.base_link = attributes.get("base_link")
        self.deck_limit = attributes.get("deck_limit")
        self.influence_limit = attributes.get("influence_limit", "")
        self.agenda_points = attributes.get("agenda_points")
        self.trash_cost = attributes.get("trash_cost")
        self.memory_cost = attributes.get("memory_cost")
        self.date_release = attributes.get("date_release")
        self.minimum_deck_size = attributes.get("minimum_deck_size")
        self.display_subtypes = attributes.get("display_subtypes", "")

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
            print(f"| Subtypes: {', '.join(self.subtypes):<56} |")
        
        if self.cost is not None:
            print(f"| Cost: {self.cost:<60} |")
        
        if self.influence_cost:
            print(f"| Influence: {self.influence_cost:<55} |")

        print(separator)

        # Card text
        if self.text:
            print("| Text: " + " " * 61 + "|")
            for line in self.format_text(self.text).split('\n'):
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
            print("| ◆ Unique                                                            |")
        
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
