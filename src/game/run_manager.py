from __future__ import annotations
import logging
from typing import List, Optional, TYPE_CHECKING
from .gamephase import GamePhase
from ..cards.base import Card
from ..cards.card_types import ICE, Agenda


if TYPE_CHECKING:
    from .game import Game
    from ..players.player import Runner
    from ..cards.card_types import ICE, Agenda

import random

logger = logging.getLogger(__name__)


class RunManager:
    def __init__(self, game: Game):
        self.game = game
        self.current_ice: Optional[ICE] = None
        self.accessed_cards: List[Card] = []

    def initiate_run(self, runner: Runner, server: str):
        logger.info(f"{runner.name} initiates a run on {server}")
        self.game.current_phase = GamePhase.RUN_INITIATION
        runner.gain_credits(self.game.corp.bad_publicity)

        ice_list = self.get_ice_protecting_server(server)

        if self.handle_confrontation_phase(ice_list):
            self.handle_access_phase(server)

        self.conclude_run()

    def get_ice_protecting_server(self, server: str):
        if server == "HQ":
            return self.game.corp.hq.ice
        elif server == "R&D":
            return self.game.corp.rd.ice
        elif server == "Archives":
            return self.game.corp.archives.ice
        else:
            try:
                return self.game.corp.remote_servers[int(server.split()[-1]) - 1].ice
            except (ValueError, IndexError):
                logger.error(f"Invalid server: {server}")
                return []

    def handle_confrontation_phase(self, ice_list):
        for ice in ice_list:
            self.game.current_phase = GamePhase.RUN_APPROACH_ICE
            self.current_ice = ice

            if self.runner_jacks_out():
                return False

            self.game.current_phase = GamePhase.RUN_ENCOUNTER_ICE
            if not self.resolve_ice_encounter(ice):
                return False

        return True

    def runner_jacks_out(self):
        return (
            self.game.user_input("Do you want to jack out? (y/n): ", ["y", "n"]) == "y"
        )

    def resolve_ice_encounter(self, ice: ICE):
        logger.info(f"Runner encountered {ice.name}")
        print(f"Encountered ICE: {ice.name}")
        print(f"Strength: {ice.strength}")
        print("Subroutines:")
        for i, subroutine in enumerate(ice.subroutines):
            print(f"{i+1}. {subroutine}")

        while True:
            action = self.game.user_input(
                "Choose an action: (b)reak subroutines, (e)nd run: ", ["b", "e"]
            )
            if action == "b":
                self.break_subroutines(ice)
            elif action == "e":
                logger.info("Runner chose to end the run")
                return False

        return self.check_unbroken_subroutines(ice)

    def break_subroutines(self, ice: ICE):
        icebreakers = [
            card
            for card in self.game.runner.rig["program"]
            if "icebreaker" in card.subtypes
        ]
        if not icebreakers:
            print("No icebreakers available to break subroutines.")
            return

        print("Available icebreakers:")
        for i, icebreaker in enumerate(icebreakers):
            print(f"{i+1}. {icebreaker.name} (Strength: {icebreaker.strength})")

        try:
            choice = (
                int(self.game.user_input("Choose an icebreaker (0 to cancel): ")) - 1
            )
            if 0 <= choice < len(icebreakers):
                icebreaker = icebreakers[choice]
                if icebreaker.strength >= ice.strength:
                    subroutines_to_break = self.game.user_input(
                        "Enter subroutine numbers to break (comma-separated): "
                    )
                    subroutine_indices = [
                        int(i) - 1
                        for i in subroutines_to_break.split(",")
                        if i.strip().isdigit()
                    ]
                    for index in subroutine_indices:
                        if 0 <= index < len(ice.subroutines):
                            ice.subroutines[index] = "Broken: " + ice.subroutines[index]
                    logger.info(
                        f"Subroutines {subroutine_indices} broken on {ice.name}"
                    )
                    print("Subroutines broken successfully.")
                else:
                    print(
                        f"Icebreaker strength ({icebreaker.strength}) is lower than ice strength ({ice.strength})."
                    )
            else:
                print("Invalid choice. No subroutines broken.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def check_unbroken_subroutines(self, ice: ICE):
        for subroutine in ice.subroutines:
            if not subroutine.startswith("Broken:"):
                # Here you would implement the effect of the subroutine
                logger.info(f"Unbroken subroutine triggered: {subroutine}")
                print(f"Subroutine triggered: {subroutine}")
                # If the subroutine ends the run, return False
                if "end the run" in subroutine.lower():
                    return False
        return True

    def handle_access_phase(self, server):
        self.game.current_phase = GamePhase.RUN_SUCCESS
        logger.info(f"Run successful. Accessing {server}")

        if server == "HQ":
            self.accessed_cards = self.access_hq()
        elif server == "R&D":
            self.accessed_cards = self.access_rd()
        elif server == "Archives":
            self.accessed_cards = self.access_archives()
        else:
            server_index = int(server.split()[-1]) - 1
            self.accessed_cards = self.access_remote_server(server_index)

        for card in self.accessed_cards:
            self.handle_accessed_card(card)

    def access_hq(self):
        return [random.choice(self.game.corp.hq.cards)]

    def access_rd(self):
        return self.game.corp.rd.cards[-1:]

    def access_archives(self):
        return self.game.corp.archives.cards

    def access_remote_server(self, server_index):
        return self.game.corp.remote_servers[server_index].installed_card

    def handle_accessed_card(self, card: Card):
        logger.info(f"Accessed card: {card.name}")
        print(f"Accessed: {card.name}")
        if isinstance(card, Agenda):
            self.game.runner.score_agenda(card)
        elif (
            card.type in ["asset", "upgrade"]
            and self.game.runner.credits >= card.trash_cost
        ):
            if (
                self.game.user_input(
                    f"Trash {card.name} for {card.trash_cost} credits? (y/n): ",
                    ["y", "n"],
                )
                == "y"
            ):
                self.game.runner.credits -= card.trash_cost
                self.game.trash_card(card)

    def conclude_run(self):
        logger.info("Run concluded")
        self.game.current_phase = GamePhase.RUN_END
        self.current_ice = None
        self.accessed_cards = []
        print("Run ended.")
