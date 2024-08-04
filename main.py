from src.game.game import Game
from src.players.corp import Corp
from src.players.runner import Runner
from src.players.player import Deck
from src.cards.base import gain_credits, draw_cards
from src.cards.corp_cards import ICE, Agenda, Operation
from src.cards.runner_cards import Program, Event

def main():
    
    # Create decks
    runner_deck = Deck([
        Program("Corroder", 2, 2),
        Program("Gordian Blade", 4, 2),
        Event("Sure Gamble", 0, gain_credits(5)),
        Event("Diesel", 0, draw_cards(3)),
        Program("Corroder", 2, 2),
        Program("Gordian Blade", 4, 2),
        Event("Sure Gamble", 0, gain_credits(5)),
        Event("Diesel", 0, draw_cards(3)),
    ] )

    corp_deck = Deck([
        ICE("Wall of Static", 3, 3),
        ICE("Wall of Static", 3, 3),
        ICE("Enigma", 3, 2),
        ICE("Enigma", 3, 2),
        Agenda("Priority Requisition", 3, 2),
        Agenda("AstroScript Pilot Program", 3, 2),
        Agenda("Priority Requisition", 3, 2),
        Agenda("AstroScript Pilot Program", 3, 2),
        Operation("Hedge Fund", 5, gain_credits(9)),
        Operation("Hedge Fund", 5, gain_credits(9)),
    ])

    # Set up the game
    runner = Runner("Runner", runner_deck)
    corp = Corp("Corp", corp_deck)

    game = Game(corp, runner)
    game.start_game()


if __name__ == "__main__":
    main()