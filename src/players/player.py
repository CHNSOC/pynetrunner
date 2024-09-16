from __future__ import annotations
import readchar
from typing import Dict, List, TYPE_CHECKING


from .base_player import Player

from ..common.gamestate import PlayerType
from ..cards.deck import Deck
import src.constructs.server as Server


if TYPE_CHECKING:
    from ..game.game import Game
    from ..cards.base import Card


class Corp(Player):
    def __init__(self, deck: Deck, identity: Card):
        self._deck = deck
        self._hand = []
        self.faction = PlayerType.CORP
        self.hq = Server.HQ()
        self.rd = Server.RD()
        self.archives = Server.Archives()
        self.remote_servers: List[Server.RemoteServer] = []
        self.bad_publicity = 0

        super().__init__(deck, identity)

    @property
    def deck(self):
        return self._deck

    @deck.setter
    def deck(self, value):
        self._deck = value
        self.rd.cards = self._deck.cards

    @property
    def hand(self):
        return self._hand

    @hand.setter
    def hand(self, value):
        self._hand = value
        self.hq.cards = self._hand

    def draw(self, count=1):
        for _ in range(count):
            if self.deck:
                card = self.deck.draw()
                self.hand.append(card)

    def get_all_installed_cards(self):
        installed_cards = []
        for server in [self.hq, self.rd, self.archives] + self.remote_servers:
            installed_cards.extend(server.ice)
            installed_cards.extend(server.upgrades)
            if isinstance(server, Server.RemoteServer) and server.installed_card:
                installed_cards.append(server.installed_card)
        return installed_cards

    def use_installed_card_ability(self, game: Game):
        installed_cards = self.get_all_installed_cards()
        if not installed_cards:
            print("No installed cards to use.")
            return False

        card = game.select_card_from_list(
            cards=installed_cards, title="Activate ability"
        )

        if not card:
            return False

        return game.effect_manager.handle_click_ability(card, self)

    def __str__(self):
        return f"{super().__str__()}, Scored Area: {self.score_area}, Remote servers: {len(self.remote_servers)}"

    def take_action(self, game: Game.Game):
        while self.clicks > 0:
            game.clear_screen()
            print(f"\nCorp's turn (Clicks: {self.clicks}, Credits: {self.credits}):")
            print("d: Draw a card")
            print("c: Gain 1 credit")
            print("p: Play or install a card from hand")
            print("a: Advance a card")
            print("s: Trigger a card ability")
            print("e: Examine servers")
            print("z: Purge virus counters")
            print("q: End turn")

            key = readchar.readkey().lower()

            if key == "d" and self.clicks > 0:
                self.draw()
                self.clicks -= 1
            elif key == "c" and self.clicks > 0:
                self.gain_credits(1)
                self.clicks -= 1
            elif key == "p" and self.clicks > 0:
                card = game.select_card_from_hand(self)
                if card and self.play_card(game, card):
                    self.clicks -= 1
            elif key == "a" and self.clicks > 0:
                if self.advance_card(game):
                    self.clicks -= 1
            elif key == "s" and self.clicks > 0:
                self.use_installed_card_ability(game)
            elif key == "e":
                self.examine_servers(game)
            elif key == "z" and self.clicks >= 3:
                if self.purge_virus_counters(game):
                    self.clicks -= 3
            else:
                print("Invalid action. Try again.")

    def create_remote_server(self):
        new_server = Server.RemoteServer(
            f"Remote Server {len(self.remote_servers) + 1}"
        )
        self.remote_servers.append(new_server)
        return new_server

    def install_card(self, game: Game, card: Card, prepaid: bool = False) -> bool:
        if card.type == "ice":
            self.install_ice(game, card)
        elif card.type in ["asset", "upgrade", "agenda"]:
            if not self.install_in_server(game, card):
                return False
        else:
            print(f"Cannot install {card.type}")
            return False

        self.hand.remove(card)
        game.effect_manager.handle_card_install(card, self)
        self.clicks -= 1
        return True

    def install_ice(self, game, ice):
        servers = ["HQ", "R&D", "Archives"] + [
            f"Remote {i+1}" for i in range(len(self.remote_servers))
        ]
        servers.append("New Remote")

        for i, server in enumerate(servers):
            print(f"{i+1}: {server}")

        choice = int(input("Choose a server to protect: ")) - 1

        if choice == len(servers) - 1:
            self.remote_servers.append(Server(f"Remote {len(self.remote_servers) + 1}"))
            server = self.remote_servers[-1]
        elif choice < len(servers) - 1:
            server = self.get_server(servers[choice])
        else:
            print("Invalid choice")
            return

        install_cost = len(server.ice)
        if self.credits >= install_cost:
            self.credits -= install_cost
            server.install_ice(ice)
            print(f"{ice.name} installed protecting {server.name}")
        else:
            print("Not enough credits to install this ice")

    def get_valid_servers(self, card):
        if card.type == "agenda":
            return [f"Remote {i+1}" for i in range(len(self.remote_servers))] + [
                "New Remote"
            ]
        elif card.type == "asset":
            return [f"Remote {i+1}" for i in range(len(self.remote_servers))] + [
                "New Remote"
            ]
        elif card.type == "upgrade":
            return (
                ["HQ", "R&D", "Archives"]
                + [f"Remote {i+1}" for i in range(len(self.remote_servers))]
                + ["New Remote"]
            )
        else:
            return []

    def install_in_server(self: Corp, game, card: Card):
        valid_servers = self.get_valid_servers(card)

        if not valid_servers:
            print(f"Cannot install {card.type} in any server.")
            return

        while True:
            print(f"Valid servers for {card.name} ({card.type}):")
            for i, server in enumerate(valid_servers):
                print(f"{i+1}: {server}")
            print("q: Cancel")
            selection = input("Choose a server to install in: ")
            if selection == "q":
                return
            try:
                choice = int(selection) - 1
                if 0 <= choice < len(valid_servers):
                    break
                else:
                    print("Invalid choice. Please select a valid server.")
            except ValueError:
                print("Invalid choice. Please enter a number.")

        server_name = valid_servers[choice]
        if server_name == "New Remote":
            server = self.create_remote_server()
        else:
            server = self.get_server(server_name)

        if card.type in ["asset", "agenda"] and isinstance(server, Server.RemoteServer):
            if server.installed_card:
                try:
                    choice = input(
                        f"Server already has a card installed. Trash {server.installed_card.name} to install {card.name}? (y/n): "
                    )
                    if choice.lower() == "y":
                        print(
                            f"Trashing {server.installed_card.name} to install {card.name}."
                        )
                        self.trash(server.installed_card)
                    else:
                        print("Installation cancelled.")
                        return
                except ValueError:
                    print("Invalid choice. Installation cancelled.")
                    return
            server.installed_card = card
        elif card.type == "upgrade":
            server.upgrades.append(card)
        else:
            print(f"Cannot install {card.type} in {server.name}")
            return

        card.location = server
        print(f"{card.name} installed in {server.name}")
        return True

    def get_server(self, server_name):
        if server_name == "HQ":
            return self.hq
        elif server_name == "R&D":
            return self.rd
        elif server_name == "Archives":
            return self.archives
        else:
            return self.remote_servers[int(server_name.split()[-1]) - 1]

    def play_card(self, game: Game, card: Card):
        if card.type == "operation":
            self.play_operation(game, card)
        elif card.type in ["ice", "asset", "upgrade", "agenda"]:
            self.install_card(game, card)
        else:
            print(f"Cannot play {card.type}")

    def play_operation(self, game: Game, card: Card):
        if self.credits >= card.cost:
            self.credits -= card.cost
            print(f"Playing operation: {card.name}")

            # Trigger the card's effects
            game.effect_manager.handle_on_play(card, self)

            # Move the card to Archives
            self.handle_card_discard(card)
            self.clicks -= 1

            print(f"{card.name} has been played and moved to Archives.")
        else:
            print(f"Not enough credits to play {card.name}.")

    def advance_card(self, game: Game):
        if self.credits < 1:
            print("Not enough credits to advance a card.")
            return False

        # Get a list of advanceable cards
        advanceable_cards = self.get_advanceable_cards()

        if not advanceable_cards:
            print("No cards available to advance.")
            return False

        # Display advanceable cards
        print("Select a card to advance:")
        for i, card in enumerate(advanceable_cards):
            print(f"{i+1}: {card.name} in {card.location}")

        choice = input("Enter the number of the card to advance (or '0' to cancel): ")
        if choice == "0":
            return False

        try:
            card_index = int(choice) - 1
            selected_card = advanceable_cards[card_index]
        except (ValueError, IndexError):
            print("Invalid choice. Advancement cancelled.")
            return False

        # Advance the card
        self.credits -= 1
        selected_card.advance()
        print(
            f"Advanced {selected_card.name}. It now has {selected_card.advancement_tokens} advancement tokens."
        )

        # Check if an agenda can be scored
        if selected_card.type == "agenda" and selected_card.can_be_scored():
            if input("This agenda can be scored. Score it now? (y/n): ").lower() == "y":
                self.score_agenda(selected_card, game)

        return True

    def get_advanceable_cards(self):
        advanceable_cards = []
        for server in self.remote_servers:
            if server.installed_card and server.installed_card.can_be_advanced():
                advanceable_cards.append(server.installed_card)
        return advanceable_cards

    def score_agenda(self, agenda: Card, game):
        self.score_area.append(agenda)
        agenda.location.installed_card = None
        print(f"Scored agenda: {agenda.name} worth {agenda.agenda_points} points.")
        game.check_win_condition()

    def rez_card(self, card: Card, game: Game):
        # Check if the card is a valid type for rezzing
        if card.type not in ["ice", "asset", "upgrade"]:
            print(f"Cannot rez {card.name}: Invalid card type.")
            return False

        # Check if the card is already rezzed
        if card.is_rezzed:
            print(f"{card.name} is already rezzed.")
            return False

        # Check if the card is installed
        if not self.is_card_installed(card):
            print(f"Cannot rez {card.name}: Card is not installed.")
            return False

        # Check if the Corp has enough credits
        if self.credits < card.cost:
            print(
                f"Not enough credits to rez {card.name}. Required: {card.cost}, Available: {self.credits}"
            )
            return False

        # Check for any additional rez requirements
        if not self.check_additional_rez_requirements(card):
            return False

        # If all checks pass, proceed with rezzing
        self.credits -= card.cost
        card.is_rezzed = True
        print(f"{card.name} has been rezzed. Paid {card.cost} credits.")

        # Handle any on-rez effects
        game.effect_manager.handle_on_rez(card, self)

        return True

    def is_card_installed(self, card: Card):
        for server in [self.hq, self.rd, self.archives] + self.remote_servers:
            if card in server.ice or card in server.upgrades:
                return True
            if (
                isinstance(server, Server.RemoteServer)
                and server.installed_card == card
            ):
                return True
        return False

    def check_additional_rez_requirements(self, card: Card):
        # This method can be expanded to check for any special rezzing conditions
        # For example, some cards might require forfeiting an agenda to rez
        if hasattr(card, "additional_cost"):
            if card.additional_cost == "forfeit_agenda":
                if not self.score_area:
                    print(f"Cannot rez {card.name}: No agenda to forfeit.")
                    return False
                # Implement agenda forfeiting logic here
        return True

    def forfeit_agenda(self, agenda):
        if agenda in self.score_area:
            self.score_area.remove(agenda)
            print(f"{self.name} forfeited {agenda.name}.")

    def add_bad_publicity(self, amount):
        self.bad_publicity += amount
        print(f"{self.name} gained {amount} bad publicity.")

    def trash_resource(self, game):
        if game.runner.tags == 0:
            print("The Runner is not tagged. Cannot trash a resource.")
            return False

        if self.credits < 2:
            print("Not enough credits to trash a resource.")
            return False

        resources = game.runner.get_installed_resources()
        if not resources:
            print("The Runner has no installed resources.")
            return False

        print("Runner's installed resources:")
        for i, resource in enumerate(resources):
            print(f"{i+1}: {resource.name}")

        choice = input("Choose a resource to trash (q to cancel): ")
        if choice == "q":
            return False

        try:
            index = int(choice) - 1
            if 0 <= index < len(resources):
                resource_to_trash = resources[index]
                self.credits -= 2
                game.runner.trash_resource(resource_to_trash)
                print(f"Trashed {resource_to_trash.name}. Corp spent 2 credits.")
                return True
            else:
                print("Invalid choice.")
                return False
        except ValueError:
            print("Invalid input.")
            return False

    def purge_virus_counters(self, game):
        if self.clicks >= 3:
            self.clicks -= 3
            game.purge_all_virus_counters()
            print(f"{self.name} purged all virus counters.")
            return True
        else:
            print("Not enough clicks to purge virus counters.")
            return False

    def purge_all_virus_counters(self):
        def remove_virus_counters(card):
            if hasattr(card, "virus_counters"):
                card.virus_counters = 0

        # Remove virus counters from runner's installed cards
        for card in self.runner.rig.values():
            remove_virus_counters(card)

        # Remove virus counters from corp's installed cards
        for server in [
            self.corp.hq,
            self.corp.rd,
            self.corp.archives,
        ] + self.corp.remote_servers:
            for card in server.ice + server.upgrades:
                remove_virus_counters(card)
            if isinstance(server, Server.RemoteServer) and server.installed_card:
                remove_virus_counters(server.installed_card)

        # Trigger any "when virus counters are purged" effects
        self.effect_manager.trigger_virus_purge_effects()

        print("All virus counters have been purged.")

    def get_card_to_expose(self):
        # Implement logic to choose a card to expose
        # This could be from HQ, R&D, or installed cards
        pass

    def handle_card_discard(self, card: Card):
        self.remove_modifiers(card)
        self.archives.handle_card_discard(card)
        self.hand.remove(card)

    def examine_servers(self, game):
        servers = [self.hq, self.rd, self.archives] + self.remote_servers
        current_server = 0

        while True:
            game.clear_screen()
            print("=== Corp Servers ===")
            for i, server in enumerate(servers):
                print(f"{'> ' if i == current_server else '  '}{server.name}")

            print("\nControls:")
            print("↑/↓: Navigate servers | Enter: View server details | Q: Quit")

            key = readchar.readkey()
            if key == readchar.key.UP and current_server > 0:
                current_server -= 1
            elif key == readchar.key.DOWN and current_server < len(servers) - 1:
                current_server += 1
            elif key == readchar.key.ENTER:
                servers[current_server].examine_server(self)
            elif key.lower() == "q":
                break


class Runner(Player):
    def __init__(self, deck: Deck, identity: Card):
        self._deck: Deck = deck
        self._hand = []
        self.rig: Dict[str, List[Card]] = {
            "program": [],
            "hardware": [],
            "resource": [],
        }
        self.heap: List[Card] = []  # Trash pile
        self.grip: List[Card] = self._hand  # Hand
        self.stack: List[Card] = deck.cards  # Draw pile
        self.faction = PlayerType.RUNNER
        self.memory_units = 4
        self.base_link = 0
        self.tags = 0
        super().__init__(deck, identity)

    @property
    def deck(self):
        return self._deck

    @deck.setter
    def deck(self, value):
        self._deck = value
        self.stack = self._deck.cards

    @property
    def hand(self):
        return self._hand

    @hand.setter
    def hand(self, value):
        self._hand = value
        self.grip = self._hand

    @property
    def link(self):
        return self.base_link + sum(
            mod.amount for mod in self.stat_modifiers if mod.stat == "link"
        )

    def get_all_installed_cards(self):
        return self.rig["program"] + self.rig["hardware"] + self.rig["resource"]

    def __str__(self):
        return f"{super().__str__()}, {len(self.rig['program'])} programs, {len(self.rig['hardware'])} hardware, {len(self.rig['resource'])} resources"

    def add_tag(self, amount):
        self.tags += amount
        print(f"{self.name} received {amount} tag{'s' if amount > 1 else ''}.")

    def remove_tag(self, count: int = 1):
        self.tags = max(0, self.tags - count)

    def take_action(self, game: Game.Game):
        while self.clicks > 0:
            game.clear_screen()
            print(f"\nRunner's turn (Clicks: {self.clicks}, Credits: {self.credits}):")
            print("d: Draw a card")
            print("c: Gain 1 credit")
            print("p: Play a card from hand")
            print("i: Install a card")
            print("e: Examine servers")
            print("r: Make a run")
            print("u: Use an installed card ability")
            print("t: Remove a tag")
            print("q: End turn")

            key = readchar.readkey().lower()

            if key == "d" and self.clicks > 0:
                self.draw()
                self.clicks -= 1
            elif key == "c" and self.clicks > 0:
                self.gain_credits(1)
                self.clicks -= 1
            elif key == "p" and self.clicks > 0:
                card = game.select_card_from_hand(self)
                if card and self.play_card(game, card):
                    self.clicks -= 1
            elif key == "i" and self.clicks > 0:
                if card and self.install_cards(game):
                    self.clicks -= 1
            elif key == "e":
                self.examine_servers(game)
            elif key == "r" and self.clicks > 0:
                if self.make_run(game):
                    self.clicks -= 1
            elif key == "u" and self.clicks > 0:
                if self.use_installed_card_ability(game):
                    self.clicks -= 1
            elif key == "t" and self.clicks > 0 and self.tags > 0:
                self.remove_tag()
                self.clicks -= 1
            elif key == "q":
                break
            else:
                print("Invalid action. Try again.")

    def use_icebreaker(self, icebreaker, ice):
        if icebreaker.can_interact(ice):
            cost = icebreaker.effects["persistent_ability"]["cost"]
            if self.can_pay(cost):
                self.pay(cost)

    def install_cards(self, game):  # TODO: Add this to menu
        installable_cards = [
            card
            for card in self.hand
            if card.type in ["program", "hardware", "resource"]
        ]
        if not installable_cards:
            print("No cards to install.")
            return

        print("Cards you can install:")
        for i, card in enumerate(installable_cards):
            print(f"{i+1}: {card.name} (Cost: {card.cost}, Type: {card.type})")

        choice = input("Choose a card to install (or 'c' to cancel): ")
        if choice == "c":
            return

        try:
            card_index = int(choice) - 1
            if 0 <= card_index < len(installable_cards):
                card = installable_cards[card_index]
                if self.credits >= card.cost:
                    self.credits -= card.cost
                    self.install_card(card)
                    self.hand.remove(card)
                    print(f"Installed {card.name}.")
                else:
                    print("Not enough credits to install this card.")
            else:
                print("Invalid card choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def install_card(self, game: Game, card: Card, prepaid: bool = False) -> bool:
        if card.type not in ["program", "hardware", "resource"]:
            print(f"Cannot install card of type {card.type}")
            return False

        if not prepaid and self.credits < card.cost:
            print("Not enough credits to install this card.")
            return False

        if card.type == "program":
            while self.get_available_mu() < card.memory_cost:
                print(
                    "Not enough memory units. Choose a program to trash or cancel installation:"
                )
                programs = self.rig["program"]
                for i, prog in enumerate(programs):
                    print(f"{i+1}. {prog.name} (MU: {prog.memory_cost})")
                print("0. Cancel installation")

                choice = input("Enter your choice: ")
                if choice == "0":
                    return False
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(programs):
                        trashed_program = programs.pop(index)
                        print(f"Trashed {trashed_program.name}")
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Invalid input. Try again.")

        if card.type == "hardware" and card.subtypes and "console" in card.subtypes:
            if any(c for c in self.rig["hardware"] if "console" in c.subtypes):
                print("You can only have one console installed at a time.")
                return False

        self.credits -= card.cost
        self.rig[card.type.lower()].append(card)
        card.location = self.rig[card.type.lower()]
        self.hand.remove(card)
        game.effect_manager.handle_card_install(card, self)
        print(f"Installed {card.name}.")
        return True

    def get_available_mu(self):
        used_mu = sum(card.memory_cost for card in self.rig["program"])
        return self.memory_units - used_mu

    def initiate_run(self, game):
        servers = ["HQ", "R&D", "Archives"] + [
            f"Remote {i+1}" for i in range(len(game.corp.remote_servers))
        ]
        print("Available servers:")
        for i, server in enumerate(servers):
            print(f"{i+1}: {server}")

        choice = input("Choose a server to run on (or 'c' to cancel): ")
        if choice == "c":
            return

        try:
            server_index = int(choice) - 1
            if 0 <= server_index < len(servers):
                target_server = servers[server_index]
                game.run(self, target_server)
            else:
                print("Invalid server choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def play_card(self, game: Game, card: Card):
        if card.type == "event":
            print(f"Playing event: {card.name}")
            if self.play_event(game, card):
                self.handle_card_discard(card)
                print(f"{card.name} has been played and moved to the Heap.")
        elif card.type in ["program", "hardware", "resource"]:
            if self.install_card(game, card):
                print(f"{card.name} has been installed.")
        else:
            print(f"Cannot play card of type {card.type}")

    def play_event(self, game: Game, card: Card) -> bool:
        if self.credits >= card.cost:
            self.credits -= card.cost
            print(f"Playing event: {card.name}")

            # Trigger the card's effects
            game.effect_manager.handle_on_play(card, self)

            self.clicks -= 1

            print(f"{card.name} has been played and moved to Archives.")
            return True
        else:
            print(f"Not enough credits to play {card.name}.")
            return False

    def examine_servers(self, game):
        servers = [
            game.corp.hq,
            game.corp.rd,
            game.corp.archives,
        ] + game.corp.remote_servers
        current_server = 0

        while True:
            game.clear_screen()
            print("=== Corp Servers ===")
            for i, server in enumerate(servers):
                print(f"{'> ' if i == current_server else '  '}{server.name}")

            print("\nControls:")
            print("↑/↓: Navigate servers | Enter: View server details | Q: Quit")

            key = readchar.readkey()
            if key == readchar.key.UP and current_server > 0:
                current_server -= 1
            elif key == readchar.key.DOWN and current_server < len(servers) - 1:
                current_server += 1
            elif key == readchar.key.ENTER:
                servers[current_server].examine_server(self)
            elif key.lower() == "q":
                break

    def handle_card_discard(self, card: Card):
        self.hand.remove(card)
        self.remove_modifiers(card)
        self.heap.append(card)

    def get_installed_resources(self):
        return self.rig["resource"]

    def trash_resource(self, resource: Card):
        self.rig["resource"].remove(resource)
        self.heap.append(resource)
        print(f"{self.name}'s resource {resource.name} was trashed.")
