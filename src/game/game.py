import random
from typing import Dict, List, Optional
from enum import Enum, auto
import sys
import readchar

from ..players.player import Player, Deck
from ..cards.base import Card
from ..cards.card_types import ICE, Agenda, Operation, Program, Event, Hardware, Resource, Asset, Upgrade
from .run_result import RunResult


class GamePhase(Enum):
    CORP_TURN_BEGIN = auto()
    CORP_DRAW = auto()
    CORP_ACTION = auto()
    CORP_DISCARD = auto()
    CORP_TURN_END = auto()
    RUNNER_TURN_BEGIN = auto()
    RUNNER_ACTION = auto()
    RUNNER_DISCARD = auto()
    RUNNER_TURN_END = auto()
    RUN_INITIATION = auto()
    RUN_APPROACH_ICE = auto()
    RUN_ENCOUNTER_ICE = auto()
    RUN_PASS_ICE = auto()
    RUN_APPROACH_SERVER = auto()
    RUN_SUCCESS = auto()
    RUN_END = auto()


class Corp(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.remote_servers: List[List[Card]] = []
        self.hq_ice: List[Card] = []
        self.rd_ice: List[Card] = []
        self.archives_ice: List[Card] = []
        self.archives: List[Card] = []

    def __str__(self):
        return f"{super().__str__()}, Scored agendas: {self.scored_agendas}, Remote servers: {len(self.remote_servers)}"

    def take_action(self, game):
        while self.clicks > 0:
            self.display_options(game)
            key = readchar.readkey()

            if key == 'd':
                self.draw()
            elif key == 'c':
                self.gain_credits(1)
            elif key == 'p':
                self.purge_virus_counters()
            elif key.isdigit() and 1 <= int(key) <= len(self.hand):
                self.handle_card_action(game, int(key) - 1)
            elif key == readchar.key.LEFT or key == readchar.key.RIGHT:
                # Handle cursor movement
                pass
            elif key == 'q':
                break  # End turn early
            else:
                print("Invalid input. Try again.")
                continue

            self.clicks -= 1

    def display_options(self, game):
        print(f"\nCorp's turn (Clicks: {
              self.clicks}, Credits: {self.credits}):")
        print("d: Draw a card")
        print("c: Gain 1 credit")
        print("p: Purge virus counters")
        print("q: End turn")
        print("\nHand:")
        for i, card in enumerate(self.hand, 1):
            print(f"{i}: {card.name} ({card.type})")

    def handle_card_action(self, game, card_index):
        card = self.hand[card_index]
        if card.type == 'Operation':
            self.play_operation(game, card)
        elif card.type in ['ICE', 'Asset', 'Upgrade', 'Agenda']:
            self.install_card(game, card)
        else:
            print("Cannot play this card type.")

    def play_operation(self, game, card):
        if self.credits >= card.cost:
            self.credits -= card.cost
            card.play(self, game)
            self.hand.remove(card)
        else:
            print("Not enough credits to play this operation.")

    def install_card(self, game, card):
        server = input(
            "Choose a server to install (HQ/R&D/Archives/1/2/3...): ")
        self.install(card, server)

    def score_agenda(self, agenda):
        self.clicks -= 1
        self.scored_agendas += agenda.agenda_points
        print(f"{self.name} scores {agenda} for {
              agenda.agenda_points} points!")

    def install(self, card: Card, server: str):
        # Basic implementation, can be expanded later
        if server.lower() == "new":
            self.remote_servers.append([card])
        elif server.isdigit():
            server_index = int(server) - 1
            if 0 <= server_index < len(self.remote_servers):
                self.remote_servers[server_index].append(card)
        # Add logic for installing in central servers if needed


class Runner(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.rig: Dict[str, List[Card]] = {
            "program": [], "hardware": [], "resource": []}
        self.heap: List[Card] = []
        self.tags = 0

    def __str__(self):
        return f"{super().__str__()}, {len(self.rig['program'])} programs, {len(self.rig['hardware'])} hardware, {len(self.rig['resource'])} resources"

    def install(self, card: Card):
        if card.type.lower() in self.rig:
            self.rig[card.type.lower()].append(card)

    def add_tag(self, count: int = 1):
        self.tags += count

    def remove_tag(self, count: int = 1):
        self.tags = max(0, self.tags - count)

    def take_action(self, game):
        while self.clicks > 0:
            self.display_options(game)
            key = readchar.readkey()

            if key == 'd':
                self.draw()
            elif key == 'c':
                self.gain_credits(1)
            elif key == 'r':
                self.initiate_run(game)
            elif key == 't':
                self.remove_tag()
            elif key.isdigit() and 1 <= int(key) <= len(self.hand):
                self.handle_card_action(game, int(key) - 1)
            elif key == readchar.key.LEFT or key == readchar.key.RIGHT:
                # Handle cursor movement
                pass
            elif key == 'q':
                break  # End turn early
            else:
                print("Invalid input. Try again.")
                continue

            self.clicks -= 1

    def display_options(self, game):
        print(f"\nRunner's turn (Clicks: {
              self.clicks}, Credits: {self.credits}):")
        print("d: Draw a card")
        print("c: Gain 1 credit")
        print("r: Initiate a run")
        print("t: Remove a tag")
        print("q: End turn")
        print("\nHand:")
        for i, card in enumerate(self.hand, 1):
            print(f"{i}: {card.name} ({card.type})")

    def handle_card_action(self, game, card_index):
        card = self.hand[card_index]
        if card.type == 'Event':
            self.play_event(game, card)
        elif card.type in ['Program', 'Hardware', 'Resource']:
            self.install_card(game, card)
        else:
            print("Cannot play this card type.")

    def play_event(self, game, card):
        if self.credits >= card.cost:
            self.credits -= card.cost
            card.play(self, game)
            self.hand.remove(card)
        else:
            print("Not enough credits to play this event.")

    def install_card(self, game, card):
        if self.credits >= card.cost:
            self.credits -= card.cost
            self.install(card)
        else:
            print("Not enough credits to install this card.")

    def initiate_run(self, server: str) -> bool:
        if self.clicks > 0:
            self.clicks -= 1
            print(f"{self.name} is initiating a run on {server}")
            return True
        else:
            print(f"{self.name} doesn't have enough clicks to initiate a run")
            return False

    def score_agenda(self, agenda):
        print(f"{self.name} scores {agenda.name} for {
              agenda.agenda_points} points!")
        return agenda.agenda_points


class Game:
    def __init__(self, corp: Corp, runner: Runner, card_registry):
        self.corp = corp
        self.runner = runner
        self.card_registry = card_registry
        self.current_player = None
        self.turn_number = 0
        self.current_phase = None

    def quit_game(self):
        print("Thanks for playing!")
        sys.exit(0)

    def setup_game(self):
        self.corp.draw(5)
        self.runner.draw(5)
        # TODO: Implement mulligan option

    def display_hand(self, player):
        print(f"\n{player.name}'s hand:")
        for i, card in enumerate(player.hand):
            print(f"  {i}: {card.name} (Cost: {card.cost}, Type: {card.type})")

    def play_game(self):
        self.setup_game()
        while not self.is_game_over():
            self.turn_number += 1
            print(f"\n--- Turn {self.turn_number} ---")
            self.play_corp_turn()
            if self.is_game_over():
                break
            self.play_runner_turn()

    def play_corp_turn(self):
        self.current_player = self.corp
        print(f"\n{self.corp.name}'s turn")
        self.execute_phase(GamePhase.CORP_TURN_BEGIN)
        self.execute_phase(GamePhase.CORP_DRAW)
        self.corp.clicks = 3
        while self.corp.clicks > 0:
            self.execute_phase(GamePhase.CORP_ACTION)
        self.execute_phase(GamePhase.CORP_DISCARD)
        self.execute_phase(GamePhase.CORP_TURN_END)

    def play_runner_turn(self):
        self.current_player = self.runner
        print(f"\n{self.runner.name}'s turn")
        self.execute_phase(GamePhase.RUNNER_TURN_BEGIN)
        self.runner.clicks = 4
        while self.runner.clicks > 0:
            self.execute_phase(GamePhase.RUNNER_ACTION)
        self.execute_phase(GamePhase.RUNNER_DISCARD)
        self.execute_phase(GamePhase.RUNNER_TURN_END)

    def execute_phase(self, phase):
        self.current_phase = phase
        self.trigger_phase_effects()

        if phase == GamePhase.CORP_TURN_BEGIN:
            print("\n--- Corporation's Turn Begins ---")
        elif phase == GamePhase.CORP_DRAW:
            self.corp.draw()
        elif phase == GamePhase.CORP_ACTION:
            self.corp.take_action(self)
        elif phase == GamePhase.CORP_DISCARD:
            self.corp.discard_down_to_max_hand_size()
        elif phase == GamePhase.CORP_TURN_END:
            print("--- Corporation's Turn Ends ---")
        elif phase == GamePhase.RUNNER_TURN_BEGIN:
            print("\n--- Runner's Turn Begins ---")
        elif phase == GamePhase.RUNNER_ACTION:
            self.runner.take_action(self)
        elif phase == GamePhase.RUNNER_DISCARD:
            self.runner.discard_down_to_max_hand_size()
        elif phase == GamePhase.RUNNER_TURN_END:
            print("--- Runner's Turn Ends ---")

    def trigger_phase_effects(self):
        # Trigger effects for cards in play that are relevant to the current phase
        pass

    def run(self, target_server):
        self.execute_phase(GamePhase.RUN_INITIATION)

        while True:
            if self.server_has_ice():
                self.execute_phase(GamePhase.RUN_APPROACH_ICE)
                if self.runner_jacks_out():
                    break
                self.execute_phase(GamePhase.RUN_ENCOUNTER_ICE)
                if self.run_ends_due_to_ice():
                    break
                self.execute_phase(GamePhase.RUN_PASS_ICE)
            else:
                self.execute_phase(GamePhase.RUN_APPROACH_SERVER)
                if self.runner_jacks_out():
                    break
                self.execute_phase(GamePhase.RUN_SUCCESS)
                self.access_cards()
                break

        self.execute_phase(GamePhase.RUN_END)

    def server_has_ice(self) -> bool:
        if self.run_target == "HQ":
            return len(self.corp.hq_ice) > 0
        elif self.run_target == "R&D":
            return len(self.corp.rd_ice) > 0
        elif self.run_target == "Archives":
            return len(self.corp.archives_ice) > 0
        else:
            server_index = int(self.run_target.split()[-1]) - 1
            return len(self.corp.remote_servers[server_index]['ice']) > 0

    def runner_jacks_out(self) -> bool:
        return input("Do you want to jack out? (y/n): ").lower() == 'y'

    def run_ends_due_to_ice(self) -> bool:
        # For now, let's assume the run ends if the Runner can't break all subroutines
        return not self.runner_breaks_all_subroutines()

    def runner_breaks_all_subroutines(self) -> bool:
        # Simplified ice breaking mechanic
        print(f"Encountered ICE: {self.current_ice.name}")
        print(f"Strength: {self.current_ice.strength}")
        print("Subroutines:")
        for subroutine in self.current_ice.subroutines:
            print(f"- {subroutine}")

        return input("Can you break all subroutines? (y/n): ").lower() == 'y'

    def access_cards(self):
        if self.run_target == "HQ":
            self.access_hq()
        elif self.run_target == "R&D":
            self.access_rd()
        elif self.run_target == "Archives":
            self.access_archives()
        else:
            self.access_remote_server()

    def access_hq(self):
        card = random.choice(self.corp.hand)
        self.handle_accessed_card(card)

    def access_rd(self):
        card = self.corp.deck.cards[-1]  # Top card of R&D
        self.handle_accessed_card(card)

    def access_archives(self):
        for card in self.corp.archives:
            self.handle_accessed_card(card)

    def access_remote_server(self):
        server_index = int(self.run_target.split()[-1]) - 1
        server = self.corp.remote_servers[server_index]
        for card in server['cards']:
            self.handle_accessed_card(card)

    def handle_accessed_card(self, card):
        print(f"Accessed: {card.name}")
        if isinstance(card, Agenda):
            self.runner.score_agenda(card)
        elif card.type in ['Asset', 'Upgrade'] and self.runner.credits >= card.trash_cost:
            if input(f"Trash {card.name} for {card.trash_cost} credits? (y/n): ").lower() == 'y':
                self.runner.credits -= card.trash_cost
                self.corp.trash(card)

    def is_game_over(self):
        if self.corp.scored_agendas >= 7:
            print(f"Game Over: {
                  self.corp.name} wins by scoring 7 agenda points!")
            return True
        elif self.runner.scored_agendas >= 7:
            print(f"Game Over: {
                  self.runner.name} wins by stealing 7 agenda points!")
            return True
        elif len(self.corp.deck) == 0:
            print(f"Game Over: {
                  self.runner.name} wins! The Corp has no more cards to draw.")
            return True
        return False
