class Card:
    def __init__(self, card_data):
        attributes = card_data.get('attributes', {})

        self.id = card_data.get('id', '')
        self.name = attributes.get('title', '')
        self.type = attributes.get('card_type_id', '')
        self.text = attributes.get('text', '')
        self.cost = attributes.get('cost')
        self.faction = attributes.get('faction_id', '')
        self.side = attributes.get('side_id', '')
        self.strength = attributes.get('strength')
        self.stripped_text = attributes.get('stripped_text', '')
        self.is_unique = attributes.get('is_unique', False)
        self.subtypes = attributes.get('card_subtype_ids', [])
        self.influence_cost = attributes.get('influence_cost')
        self.base_link = attributes.get('base_link')
        self.deck_limit = attributes.get('deck_limit')
        self.influence_limit = attributes.get('influence_limit', '')
        self.agenda_points = attributes.get('agenda_points')
        self.trash_cost = attributes.get('trash_cost')
        self.memory_cost = attributes.get('memory_cost')
        self.date_release = attributes.get('date_release')
        self.minimum_deck_size = attributes.get('minimum_deck_size')
        self.display_subtypes = attributes.get('display_subtypes', "")

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
            f"  Trash Ability: {self.trash_ability}"
        ]
        return '\n'.join(attributes)

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


def gain_credits(amount):
    def effect(player, game):
        player.credits += amount
        print(f"{player.name} gains {amount} credits")
    return effect


def draw_cards(amount):
    def effect(player, game):
        player.draw(amount)
        print(f"{player.name} draws {amount} cards")
    return effect
