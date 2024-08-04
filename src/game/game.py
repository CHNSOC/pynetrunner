import random
from typing import List
from ..players.corp import Corp
from ..players.runner import Runner
from ..cards.base import Card
from ..cards.corp_cards import Agenda
from ..cards.runner_cards import Program, Event, Operation
from .run_result import RunResult

import sys



class Game:
    def __init__(self, corp: Corp, runner: Runner):
        self.corp = corp
        self.runner = runner
        self.current_player = self.corp
        self.runner_score = 0
        self.action_map = {
            'A': ('draw', self.draw_card),
            'B': ('gain credit', self.gain_credit),
            'C': ('install', self.install_card),
            'D': ('run', self.run),
            'E': ('score agenda', self.score_agenda),
            'F': ('play event/operation', self.play_card),
            'H': ('help', self.show_help),
            'Q': ('quit', self.quit_game)
        }

    def show_help(self):
        print("\nAvailable commands:")
        for key, (action, _) in self.action_map.items():
            print(f"({key}) {action}")
        print("(Q) Quit the game")

    def draw_card(self):
        self.current_player.clicks -= 1
        self.current_player.draw()
        print(f"{self.current_player.name} drew a card")

    def gain_credit(self):
        self.current_player.clicks -= 1
        self.current_player.credits += 1
        print(f"{self.current_player.name} gained 1 credit")

    def handle_run(self, server: str) -> RunResult:
        if not self.runner.initiate_run(server):
            return RunResult(False, [], "Not enough clicks to initiate run")

        accessed_cards = []
        if server == "R&D":
            accessed_cards = self.corp.deck.cards[-1:]
        elif server == "HQ":
            accessed_cards = random.sample(self.corp.hand, 1) if self.corp.hand else []
        elif server == "Archives":
            accessed_cards = self.corp.archives
        else:
            return RunResult(False, [], f"Invalid server: {server}")

        self.runner.access_cards(accessed_cards)

        for card in accessed_cards:
            if isinstance(card, Agenda):
                points = self.runner.score_agenda(card)
                self.runner_score += points
                return RunResult(True, accessed_cards, f"Run successful, scored agenda: {card.name}")

        return RunResult(True, accessed_cards, "Run successful, no agenda scored")

    def install_card(self):
        if self.current_player.hand:
            card_index = int(
                input(f"Choose a card to install (0-{len(self.current_player.hand)-1}): "))
            card = self.current_player.hand[card_index]
            if isinstance(self.current_player, Runner) and isinstance(card, Program):
                self.current_player.install_program(card)
            elif isinstance(self.current_player, Corp):
                server = input(
                    "Choose a server to install in (leave blank for new remote): ")
                self.current_player.install_card(
                    card, int(server) if server else None)
        else:
            print("No cards in hand to install")

    def run(self):
        if isinstance(self.current_player, Runner):
            server = input("Choose a server to run on (HQ, R&D, Archives): ")
            self.current_player.run(server, self)
        else:
            print("Only the Runner can make runs")

    def score_agenda(self):
        if isinstance(self.current_player, Corp):
            if any(isinstance(card, Agenda) for server in self.current_player.remote_servers for card in server):
                server_index = int(
                    input("Choose a server with an agenda to score: "))
                agenda = next(
                    card for card in self.current_player.remote_servers[server_index] if isinstance(card, Agenda))
                self.current_player.score_agenda(agenda)
            else:
                print("No agendas available to score")
        else:
            print("Only the Corp can score agendas")

    def play_card(self):
        if isinstance(self.current_player, Runner):
            events = [
                card for card in self.current_player.hand if isinstance(card, Event)]
            if events:
                event_index = int(
                    input(f"Choose an event to play (0-{len(events)-1}): "))
                events[event_index].play(self.current_player, self)
            else:
                print("No events in hand to play")
        elif isinstance(self.current_player, Corp):
            operations = [
                card for card in self.current_player.hand if isinstance(card, Operation)]
            if operations:
                operation_index = int(
                    input(f"Choose an operation to play (0-{len(operations)-1}): "))
                operations[operation_index].play(self.current_player, self)
            else:
                print("No operations in hand to play")

    def quit_game(self):
        print("Thanks for playing!")
        sys.exit(0)

    def start_game(self):
        self.corp.draw(5)
        self.runner.draw(5)
        self.show_help()
        while not self.game_over():
            try:
                self.play_turn()
            except SystemExit:
                break  # Exit the game loop if the quit command is used

    def display_hand(self, player):
        print(f"\n{player.name}'s hand:")
        for i, card in enumerate(player.hand):
            print(f"  {i}: {card.name} (Cost: {card.cost}, Type: {card.type})")

    def play_turn(self):
        self.current_player.clicks = 3 if isinstance(self.current_player, Runner) else 4
        self.current_player.credits += 1
        print(f"\n--- {self.current_player.name}'s turn ---")
        print(f"Credits: {self.current_player.credits}, Clicks: {self.current_player.clicks}")
        
        # Display the current player's hand
        self.display_hand(self.current_player)

        while self.current_player.clicks > 0:
            self.perform_action()

        self.end_turn()

    def perform_action(self):
        while True:
            action = input("Choose an action (H for help): ").upper()
            if action in self.action_map:
                _, func = self.action_map[action]
                if action == 'D':  # Assuming 'D' is for run
                    server = input("Choose a server to run on (HQ, R&D, Archives): ")
                    result = self.handle_run(server)
                    print(result.message)
                else:
                    func()
                self.display_hand(self.current_player)
                break
            else:
                print("Invalid action. Press H for help.")

    def end_turn(self):
        self.current_player = self.runner if isinstance(
            self.current_player, Corp) else self.corp

    def game_over(self) -> bool:
        if self.corp.scored_agendas >= 7:
            print(f"{self.corp.name} wins by scoring 7 agenda points!")
            return True
        elif self.runner_score >= 7:
            print(f"{self.runner.name} wins by scoring 7 agenda points!")
            return True
        elif len(self.corp.deck.cards) == 0:
            print(f"{self.runner.name} wins! The Corp has no more cards to draw.")
            return True
        return False