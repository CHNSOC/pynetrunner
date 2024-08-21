import random

import sys
import os
import readchar

from ..cards.base import Card

from ..cards.card_types import (
    Agenda,
)

from .gamephase import GamePhase
from ..effects.effect_manager import EffectManager, GlobalEffect
from ..players.player import Corp, Runner
import src.players.player as Player
from ..constructs.server import RemoteServer


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
            self.effect_manager.add_global_effect(player.identity)

    def corp_mulligan_decision(self):
        self.display_hand(self.corp, "Mulligan Phase")
        return input("Corporation: Do you want to mulligan? (y/n): ").lower() == "y"

    def runner_mulligan_decision(self):
        self.display_hand(self.runner, "Mulligan Phase")
        return input("Runner: Do you want to mulligan? (y/n): ").lower() == "y"

    def display_hand(self, player: Player, phase=None):
        detailed = False
        current_card = 0

        while True:
            self.clear_screen()
            if phase:
                print(f"--- {phase} ---")
            print(f"\n{player.name}'s hand ({len(player.hand)} cards):")

            for i, card in enumerate(player.hand):
                if i == current_card:
                    print("> ", end="")
                else:
                    print("  ", end="")

                basic_info = f"{i + 1}: {card.name} ({card.type})"

                if isinstance(player, Corp):
                    basic_info += f" - Rez Cost: {card.cost}"
                else:
                    basic_info += f" - Install Cost: {card.cost}"

                if card.type == "ice":
                    basic_info += f", Strength: {card.strength}"
                elif card.type == "agenda":
                    basic_info += f", Advance Req: {card.advancement_requirement}, Agenda Points: {card.agenda_points}"

                print(basic_info)

                if detailed and i == current_card:
                    if card.subtypes:
                        print(f"   Subtypes: {', '.join(card.subtypes)}")
                    if card.type == "ice" and hasattr(card, "subroutines"):
                        print("   Subroutines:")
                        for subroutine in card.subroutines:
                            print(f"    [⊡] {subroutine}")
                    elif card.stripped_text:
                        print(f"   Effect: {card.stripped_text}")
                    if card.type in ["asset", "upgrade"] and hasattr(
                        card, "trash_cost"
                    ):
                        print(f"   Trash Cost: {card.trash_cost}")
                    print()  # Add a blank line for readability in detailed view

            if isinstance(player, Runner):
                print(
                    f"\nInstalled: Programs: {len(player.rig['program'])}, Hardware: {len(player.rig['hardware'])}, Resources: {len(player.rig['resource'])}"
                )
            elif isinstance(player, Corp):
                total_ice = sum(
                    len(server.ice)
                    for server in [player.hq, player.rd, player.archives]
                    + player.remote_servers
                )
                total_assets_upgrades = sum(
                    len(server.upgrades)
                    for server in [player.hq, player.rd, player.archives]
                    + player.remote_servers
                )
                total_assets_upgrades += sum(
                    1
                    for server in player.remote_servers
                    if server.installed_card is not None
                )
                print(
                    f"\nInstalled: Ice: {total_ice}, Assets/Upgrades/Agendas: {total_assets_upgrades}"
                )

            print("\nControls:")
            print(
                "↑/↓: Navigate cards | D: Toggle detailed view | Q: Quit | Enter: Select card"
            )

            key = readchar.readkey()
            if key == readchar.key.UP and current_card > 0:
                current_card -= 1
            elif key == readchar.key.DOWN and current_card < len(player.hand) - 1:
                current_card += 1
            elif key.lower() == "d":
                detailed = not detailed
            elif key.lower() == "q":
                break
            elif key == readchar.key.ENTER:
                return player.hand[current_card]

        return None

    def select_card_from_hand(self, player):
        selected_card = self.display_hand(player, self.current_phase)
        return selected_card

    def display_runner_resources(self):
        resources = self.runner.get_installed_resources()
        if not resources:
            print("The Runner has no installed resources.")
        else:
            print("Runner's installed resources:")
            for i, resource in enumerate(resources):
                print(f"{i+1}: {resource.name}")

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

    def run(self, runner, server):
        print(f"{runner.name} initiates a run on {server}")

        # 1. Initiation Phase
        self.current_phase = GamePhase.RUN_INITIATION
        runner.gain_credits(self.corp.bad_publicity)

        ice_list = self.get_ice_protecting_server(server)

        # 2. Confrontation Phase
        for ice in ice_list:
            self.current_phase = GamePhase.RUN_APPROACH_ICE
            if runner.decide_to_continue():
                self.current_phase = GamePhase.RUN_ENCOUNTER_ICE
                runner.encounter_ice(ice)
            else:
                print(f"{runner.name} jacks out.")
                return

        # 3. Access Phase
        self.current_phase = GamePhase.RUN_SUCCESS
        accessed_cards = self.access_server(server)
        for card in accessed_cards:
            self.handle_accessed_card(card)

        print(f"Run on {server} successful.")

    def get_ice_protecting_server(self, server):
        if server == "HQ":
            return self.corp.hq.ice
        elif server == "R&D":
            return self.corp.rd.ice
        elif server == "Archives":
            return self.corp.archives.ice
        else:
            return self.corp.remote_servers[int(server.split()[-1]) - 1].ice

    def access_server(self, server):
        if server == "HQ":
            return [random.choice(self.corp.hand)]
        elif server == "R&D":
            return [self.corp.deck.cards[-1]]
        elif server == "Archives":
            return self.corp.archives.cards
        else:
            return self.corp.remote_servers[int(server.split()[-1]) - 1].cards

    def handle_accessed_card(self, card):
        print(f"Accessed: {card.name}")
        if isinstance(card, Agenda):
            self.runner.score_agenda(card)
        elif (
            card.type in ["asset", "upgrade"] and self.runner.credits >= card.trash_cost
        ):
            if (
                input(
                    f"Trash {card.name} for {card.trash_cost} credits? (y/n): "
                ).lower()
                == "y"
            ):
                self.runner.credits -= card.trash_cost
                self.corp.trash(card)

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

    def purge_all_virus_counters(self):
        # Remove virus counters from all installed cards
        for card in (
            self.corp.get_all_installed_cards() + self.runner.get_all_installed_cards()
        ):
            if hasattr(card, "virus_counters"):
                card.virus_counters = 0

        # Trigger any "when virus counters are purged" effects
        self.effect_manager.trigger_virus_purge_effects()

        print("All virus counters have been purged.")

    def corp_rez_opportunity(self):
        while True:
            print("\nRez opportunity:")
            unrezzed_cards = self.get_unrezzed_corp_cards()
            for i, card in enumerate(unrezzed_cards):
                print(f"{i+1}. {card.name} (Rez cost: {card.cost})")
            print("0. Done rezzing")

            choice = input("Choose a card to rez (or 0 to finish): ")
            if choice == "0":
                break
            try:
                card_index = int(choice) - 1
                if 0 <= card_index < len(unrezzed_cards):
                    self.corp.rez_card(unrezzed_cards[card_index], self)
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Try again.")

    def get_unrezzed_corp_cards(self):
        unrezzed_cards = []
        for server in [
            self.corp.hq,
            self.corp.rd,
            self.corp.archives,
        ] + self.corp.remote_servers:
            unrezzed_cards.extend([ice for ice in server.ice if not ice.is_rezzed])
            unrezzed_cards.extend(
                [upgrade for upgrade in server.upgrades if not upgrade.is_rezzed]
            )
            if (
                isinstance(server, RemoteServer)
                and server.installed_card
                and hasattr(server.installed_card, "is_rezzed")
                and not server.installed_card.is_rezzed
            ):
                unrezzed_cards.append(server.installed_card)
        return unrezzed_cards

    def access_hq(self):
        return [random.choice(self.corp.hq.cards)]

    def access_rd(self):
        return self.corp.rd.cards[-1:]

    def access_archives(self):
        return self.corp.archives.cards

    def access_remote_server(self, server_index):
        return self.corp.remote_servers[server_index].cards

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
            if isinstance(player, Corp):
                player.play_card(self, card)  # ???
            else:
                # Handle Runner card play
                pass
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
        self.check_win_condition()

    def discard_down_to_max_hand_size(self, player: Player):
        while len(player.hand) > player.get_max_hand_size():
            self.display_hand(player, self.current_phase)
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
            player.handle_card_discard(player.hand[card_index])

    def check_win_condition(self):
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
        while not self.check_win_condition():
            self.turn_number += 1
            print(f"\n--- Turn {self.turn_number} ---")
            self.play_corp_turn()
            if self.check_win_condition():
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
            self.corp_rez_opportunity()
        self.execute_phase(GamePhase.CORP_DISCARD)
        self.corp_rez_opportunity()
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

    def get_all_active_cards(self):
        active_cards = []

        # Corp cards
        active_cards.extend(self.corp.score_area)

        # Corp Identity
        active_cards.append(self.corp.identity)

        # Corp servers
        for server in [
            self.corp.hq,
            self.corp.rd,
            self.corp.archives,
        ] + self.corp.remote_servers:
            active_cards.extend(server.ice)
            active_cards.extend(server.upgrades)
            if isinstance(server, RemoteServer) and server.installed_card:
                active_cards.append(server.installed_card)

        # Runner cards
        active_cards.extend(self.runner.score_area)

        # Runner Identity
        active_cards.append(self.runner.identity)

        # Runner resources
        active_cards.extend(self.runner.rig["program"])
        active_cards.extend(self.runner.rig["hardware"])
        active_cards.extend(self.runner.rig["resource"])

        return active_cards

    def execute_phase(self, phase: GamePhase):
        self.current_phase = phase
        effect_manager: EffectManager = self.effect_manager

        corp_effects = self.corp.get_active_effects(phase)
        for card, effect in corp_effects:
            effect_manager.handle_effect(effect, card)

        # Handle Runner's active effects
        runner_effects = self.runner.get_active_effects(phase)
        for card, effect in runner_effects:
            effect_manager.handle_effect(effect, card)

        if phase == GamePhase.CORP_TURN_BEGIN:
            print("\n--- Corporation's Turn Begins ---")
            effect_manager.trigger_phase_effects("corp_turn_begin")
        elif phase == GamePhase.CORP_DRAW:
            effect_manager.trigger_phase_effects("corp_draw")
            self.corp.draw(1)
        elif phase == GamePhase.CORP_ACTION:
            self.corp.take_action(self)
            effect_manager.trigger_phase_effects("corp_action")
        elif phase == GamePhase.CORP_DISCARD:
            effect_manager.trigger_phase_effects("corp_discard")
            self.discard_down_to_max_hand_size(self.corp)
        elif phase == GamePhase.CORP_TURN_END:
            effect_manager.trigger_phase_effects("corp_turn_end")
            print("--- Corporation's Turn Ends ---")
        elif phase == GamePhase.RUNNER_TURN_BEGIN:
            effect_manager.trigger_phase_effects("runner_turn_begin")
            print("\n--- Runner's Turn Begins ---")
        elif phase == GamePhase.RUNNER_ACTION:
            self.runner.take_action(self)
            effect_manager.trigger_phase_effects("runner_action")
            pass
        elif phase == GamePhase.RUNNER_DISCARD:
            effect_manager.trigger_phase_effects("runner_discard")
            self.discard_down_to_max_hand_size(self.runner)
        elif phase == GamePhase.RUNNER_TURN_END:
            effect_manager.trigger_phase_effects("runner_turn_end")
            print("--- Runner's Turn Ends ---")

    def clear_screen(self):
        # os.system("cls" if os.name == "nt" else "clear")
        print("\n\n\n")
        pass
