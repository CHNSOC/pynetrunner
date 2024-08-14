import random
from enum import Enum, auto
import sys
import readchar

from ..cards.base import Card

from ..cards.card_types import (
    Agenda,
)
from .run_result import RunResult
from ..effects.effect_manager import EffectManager, GlobalEffect
import src.players.player as Player


class Game:
    def __init__(self, corp, runner, card_registry):
        self.corp = corp
        self.runner = runner
        self.card_registry = card_registry
        self.current_player = None
        self.turn_number = 0
        self.current_phase = None
        self.effect_manager = EffectManager(self)
        self.setup_identities()

    def quit_game(self):
        print("Thanks for playing!")
        sys.exit(0)

    def setup_game(self):
        self.corp.draw(5)
        self.runner.draw(5)

        self.setup_identities()

        # Corp mulligan
        if not self.corp.has_mulliganed and self.corp_mulligan_decision():
            self.corp.mulligan()

        # Runner mulligan
        if not self.runner.has_mulliganed and self.runner_mulligan_decision():
            self.runner.mulligan()

    def add_global_effect(self, effect):
        self.effect_manager.add_global_effect(effect)

    def setup_identities(self):
        self.setup_identity(self.corp)
        self.setup_identity(self.runner)

    def setup_identity(self, player: Player):
        if player.identity:
            identity_effects = player.identity.effects.get("persistent", [])
            for effect in identity_effects:
                self.effect_manager.add_global_effect(
                    GlobalEffect(effect["trigger"], effect)
                )

    def corp_mulligan_decision(self):
        self.display_hand(self.corp)
        return input("Corporation: Do you want to mulligan? (y/n): ").lower() == "y"

    def runner_mulligan_decision(self):
        self.display_hand(self.runner)
        return input("Runner: Do you want to mulligan? (y/n): ").lower() == "y"

    def display_hand(self, player: Player):
        print(f"\n{player.name}'s hand:\n")
        for i, card in enumerate(player.hand):
            print(
                f"  {i + 1}: {card.name} (Cost: {card.cost}, Type: {card.type})\n\t {card.stripped_text}"
            )

    def play_card(self, player: Player.Corp | Player.Runner, card: Card):
        # This handles playing a card from the player's hand
        if player == self.corp:
            if card.type == "operation":
                self.effect_manager.handle_on_play(card, player)
                self.effect_manager.trigger_global_effects(
                    "operation_played", player=player, card=card
                )
            elif (
                card.type == "ice"
                or card.type == "asset"
                or card.type == "upgrade"
                or card.type == "agenda"
            ):
                player.install_card(self, card)
        player.handle_card_discard(card)

    def trigger_phase_effects(self):
        # Trigger effects for cards in play that are relevant to the current phase
        pass

    def handle_on_rez_effect(self, card):
        effect = card.effects.get("on_rez")
        if effect:
            self.apply_effect(effect, card)

    def handle_on_turn_begin_effect(self, card):
        effect = card.effects.get("on_turn_begin")
        if effect:
            self.apply_effect(effect, card)

    def handle_on_token_empty_effect(self, card):
        effect = card.effects.get("on_token_empty")
        if effect:
            self.apply_effect(effect, card)

    def handle_on_play_effect(self, card):
        effect = card.effects.get("on_play")
        if effect:
            self.apply_effect(effect, card)

    def apply_effect(self, effect, card):
        action = effect.get("action")
        amount = effect.get("amount")

        if action == "place_credits":
            card.credits = amount
        elif action == "gain_credits":
            self.current_player.credits += amount
        elif action == "trash_self":
            self.current_player.trash(card)
        # Add more actions as needed

    def run(self, runner, server):
        self.current_phase = GamePhase.RUN_INITIATION
        ice_list = self.get_ice_protecting_server(server)

        for ice in ice_list:
            self.current_phase = GamePhase.RUN_APPROACH_ICE
            if runner.decide_to_continue():
                self.current_phase = GamePhase.RUN_ENCOUNTER_ICE
                runner.encounter_ice(ice)
            else:
                return RunResult(False, [], "Runner jacked out")

        self.current_phase = GamePhase.RUN_SUCCESS
        accessed_cards = self.access_server(server)
        return RunResult(True, accessed_cards, "Run successful")

    def get_ice_protecting_server(self, server):
        if server == "HQ":
            return self.corp.hq.ice
        elif server == "R&D":
            return self.corp.rd.ice
        elif server == "Archives":
            return self.corp.archives.ice
        else:
            return self.corp.remote_servers[int(server)].ice

    def server_has_ice(self) -> bool:
        if self.run_target == "HQ":
            return len(self.corp.hq_ice) > 0
        elif self.run_target == "R&D":
            return len(self.corp.rd_ice) > 0
        elif self.run_target == "Archives":
            return len(self.corp.archives_ice) > 0
        else:
            server_index = int(self.run_target.split()[-1]) - 1
            return len(self.corp.remote_servers[server_index]["ice"]) > 0

    def resolve_subroutines(self, ice):
        for subroutine in ice.effects.get("subroutines", []):
            action = subroutine.get("action")
            if action == "lose_click":
                self.runner.clicks -= 1
            elif action == "end_run":
                return True  # End the run
        return False  # Continue the run

    def runner_jacks_out(self) -> bool:
        return input("Do you want to jack out? (y/n): ").lower() == "y"

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

        return input("Can you break all subroutines? (y/n): ").lower() == "y"

    def access_server(self, server):
        if server == "HQ":
            return self.access_hq()
        elif server == "R&D":
            return self.access_rd()
        elif server == "Archives":
            return self.access_archives()
        else:
            return self.access_remote_server(int(server))

    def access_hq(self):
        return [random.choice(self.corp.hq.cards)]

    def access_rd(self):
        return self.corp.rd.cards[-1:]

    def access_archives(self):
        return self.corp.archives.cards

    def access_remote_server(self, server_index):
        return self.corp.remote_servers[server_index].cards

    def handle_accessed_card(self, card):
        print(f"Accessed: {card.name}")
        if isinstance(card, Agenda):
            self.runner.score_agenda(card)
        elif (
            card.type in ["Asset", "Upgrade"] and self.runner.credits >= card.trash_cost
        ):
            if (
                input(
                    f"Trash {card.name} for {card.trash_cost} credits? (y/n): "
                ).lower()
                == "y"
            ):
                self.runner.credits -= card.trash_cost
                self.corp.trash(card)

    def calculate_score(self, score_area):
        if not score_area:
            return 0
        return sum([card.agenda_points for card in score_area])

    def handle_card_operation(self, player: Player, card: Card):
        card.pretty_print()
        print("\n")
        print("What would you like to do?")
        print("p: Play card")
        print("q: Return")
        key = readchar.readkey()
        if key == "p":
            self.play_card(player, card)
        elif key == "q":
            return

    def score_agenda(self, agenda, player):
        if player == self.corp:
            self.corp.score_area.append(agenda)
            self.corp.hand.remove(agenda)
        self.update_score()
        self.effect_manager.trigger_global_effects(
            "agenda_scored_or_stolen", player=player
        )
        self.handle_agenda_effects(agenda, "scored")

    def steal_agenda(self, agenda, player):
        if player == self.runner:
            self.runner.score_area.append(agenda)
            # Remove from appropriate Corp zone (server, R&D, etc.)
        self.update_score()
        self.effect_manager.trigger_global_effects(
            "agenda_scored_or_stolen", player=player
        )
        self.handle_agenda_effects(agenda, "stolen")

    def handle_agenda_effects(self, agenda, action):
        if action == "scored":
            self.effect_manager.handle_on_score(agenda, self.corp)
        elif action == "stolen":
            self.effect_manager.handle_on_steal(agenda, self.runner)

    def update_score(self):
        self.corp_score = sum(agenda.points for agenda in self.corp.score_area)
        self.runner_score = sum(agenda.points for agenda in self.runner.score_area)
        self.is_game_over()

    def discard_down_to_max_hand_size(self, player: Player):
        while len(player.hand) > player.get_max_hand_size():
            self.display_hand(player)
            max_hand_size = player.get_max_hand_size()
            user_selection = input(
                f"You have {len(player.hand)} cards. Discard down to { max_hand_size}. Choose a card to discard: "
            )
            if not user_selection.isdigit():
                print("Invalid card index. Try again.")
                continue
            card_index = int(user_selection) - 1
            if not 0 <= card_index < len(player.hand):
                print("Invalid card index. Try again.")
                continue
            discarded_card = player.hand.pop(card_index)
            player.handle_card_discard(discarded_card)

    def is_game_over(self):
        if self.calculate_score(self.corp.score_area) >= 7:
            print(f"Game Over: {self.corp.name} wins by scoring 7 agenda points!")
            return True
        elif self.calculate_score(self.runner.score_area) >= 7:
            print(f"Game Over: {self.runner.name} wins by stealing 7 agenda points!")
            return True
        elif len(self.corp.deck) == 0:
            print(
                f"Game Over: {self.runner.name} wins! The Corp has no more cards to draw."
            )
            return True
        return False

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
            if self.is_game_over():
                return
            self.corp.draw(1)
        elif phase == GamePhase.CORP_ACTION:
            self.corp.take_action(self)
            pass
        elif phase == GamePhase.CORP_DISCARD:
            self.discard_down_to_max_hand_size(self.corp)
        elif phase == GamePhase.CORP_TURN_END:
            print("--- Corporation's Turn Ends ---")
        elif phase == GamePhase.RUNNER_TURN_BEGIN:
            print("\n--- Runner's Turn Begins ---")
        elif phase == GamePhase.RUNNER_ACTION:
            self.runner.take_action(self)
            pass
        elif phase == GamePhase.RUNNER_DISCARD:
            self.discard_down_to_max_hand_size(self.runner)
        elif phase == GamePhase.RUNNER_TURN_END:
            print("--- Runner's Turn Ends ---")


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
