import json
from src.game.game import Game
from src.players.player import Corp, Runner
from src.players.player import Deck
from src.cards.card_registry import CardRegistry


def create_deck_from_card_ids(registry, card_ids):
    return Deck([registry.get_card(card_id) for card_id in card_ids])


def load_deck_from_json(file_path: str, card_registry: CardRegistry) -> Deck:
    with open(file_path, "r") as file:
        deck_data = json.load(file)
    identity = deck_data["identity"]
    cards = []
    for card_entry in deck_data["cards"]:
        card = card_registry.get_card(card_entry["id"])
        if card:
            cards.extend([card] * card_entry["quantity"])
        else:
            print(f"Warning: Card with ID {card_entry['id']} not found in registry")

    return Deck(cards), identity


def setup_players():
    card_registry = CardRegistry()
    card_registry.load_cards_from_json(
        "assets/cards/core_set.json", "assets/cards/card_effects.json"
    )

    # Set up Corp
    corp_deck, corp_identity = load_deck_from_json(
        "assets/decks/corp/weyland_starter.json", card_registry
    )

    corp = Corp(corp_deck, card_registry.get_card(corp_identity))

    # Set up Runner
    runner_deck, runner_identity = load_deck_from_json(
        "assets/decks/runner/shaper_starter.json", card_registry
    )
    runner = Runner(runner_deck, card_registry.get_card(runner_identity))

    game = Game(corp, runner, card_registry)
    return game


if __name__ == "__main__":
    game = setup_players()
    game.play_game()
