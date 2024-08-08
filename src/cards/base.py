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
        self.advancement_requirement = attributes.get(
            'advancement_requirement')
        self.agenda_points = attributes.get('agenda_points')
        self.trash_cost = attributes.get('trash_cost')
        self.memory_cost = attributes.get('memory_cost')
        self.date_release = attributes.get('date_release')
        self.minimum_deck_size = attributes.get('minimum_deck_size')
        self.display_subtypes = attributes.get('display_subtypes', "")

        # Add card_abilities
        self.card_abilities = attributes.get('card_abilities', {})

        # For easier access, we can also add individual attributes for each ability
        self.additional_cost = self.card_abilities.get(
            'additional_cost', False)
        self.advanceable = self.card_abilities.get('advanceable', False)
        self.gains_subroutines = self.card_abilities.get(
            'gains_subroutines', False)
        self.interrupt = self.card_abilities.get('interrupt', False)
        self.link_provided = self.card_abilities.get('link_provided')
        self.mu_provided = self.card_abilities.get('mu_provided')
        self.num_printed_subroutines = self.card_abilities.get(
            'num_printed_subroutines', 0)
        self.on_encounter_effect = self.card_abilities.get(
            'on_encounter_effect', False)
        self.performs_trace = self.card_abilities.get('performs_trace', False)
        self.recurring_credits_provided = self.card_abilities.get(
            'recurring_credits_provided')
        self.rez_effect = self.card_abilities.get('rez_effect', False)
        self.trash_ability = self.card_abilities.get('trash_ability', False)

    def play(self, player, game):
        if player.credits >= self.cost:
            player.credits -= self.cost
            player.clicks -= 1
            self.effect(player, game)
            return True
        return False

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
