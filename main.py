import json
from src.game.game import Game, Corp, Runner
from src.players.player import Deck
from src.cards.base import gain_credits, draw_cards
from src.cards.card_registry import CardRegistry


def create_deck_from_card_ids(registry, card_ids):
    return Deck([registry.get_card(card_id) for card_id in card_ids])


def load_deck_from_json(file_path: str, card_registry: CardRegistry) -> Deck:
    with open(file_path, 'r') as file:
        deck_data = json.load(file)

    cards = []
    for card_entry in deck_data['cards']:
        card = card_registry.get_card(card_entry['id'])
        if card:
            cards.extend([card] * card_entry['quantity'])
        else:
            print(f"Warning: Card with ID {
                  card_entry['id']} not found in registry")

    return Deck(cards)


def setup_game():
    card_registry = CardRegistry()
    card_registry.load_cards_from_json('assets/cards/core_set.json')

    # Set up Corp
    corp_deck = load_deck_from_json(
        'assets/decks/corp/weyland_starter.json', card_registry)
    corp_identity = card_registry.get_card(
        'weyland_consortium_building_a_better_world')
    corp = Corp(corp_identity.name, corp_deck)

    # Set up Runner
    runner_deck = load_deck_from_json(
        'assets/decks/runner/shaper_starter.json', card_registry)
    runner_identity = card_registry.get_card(
        'kate_mac_mccaffrey_digital_tinker')
    runner = Runner(runner_identity.name, runner_deck)

    game = Game(corp, runner, card_registry)
    return game


if __name__ == "__main__":
    game = setup_game()
    game.play_game()
