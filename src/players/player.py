import readchar
import random
from typing import Dict, List, Optional
from random import shuffle

from ..cards.base import Card
import src.game.game as Game
from ..constructs.server import Server, Archives


class Deck:
    def __init__(self, cards: List[Card]):
        self.cards = cards
        shuffle(self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None

    def add_card(self, card: Card):
        self.cards.append(card)


class Player:
    def __init__(self, deck: Deck, identity: Optional[Card] = None):
        self.name = identity.name if identity else "Anonymous"
        self.deck = deck
        self.identity = identity
        self.hand: List[Card] = []
        self.credits = 5
        self.clicks = 0
        self.has_mulliganed = False
        self.score_area: List[Card] = []
        self.installed_cards = []

    def __str__(self):
        return f"{self.name} - Credits: {self.credits}, Clicks: {self.clicks}, Hand size: {len(self.hand)}"

    def draw(self, count: int = 1):
        for _ in range(count):
            if self.deck:
                self.hand.append(self.deck.draw())
            else:
                # Handle deck out situation
                pass

    def mulligan(self):
        if not self.has_mulliganed:
            # Return all cards to the deck
            self.deck.cards.extend(self.hand)
            self.hand.clear()
            # Shuffle the deck
            random.shuffle(self.deck.cards)
            # Draw a new hand
            self.draw(5)
            self.has_mulliganed = True
        else:
            print(f"{self.name} has already mulliganed in this game.")

    def set_identity(self, identity_card):
        self.identity = identity_card

    def gain_credits(self, amount: int):
        self.credits += amount

    def spend_credits(self, amount: int):
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False

    def get_max_hand_size(self) -> int:
        # Implement logic to calculate max hand size, including card effects
        return 5

    def get_active_effects(self, phase):
        active_effects = []
        for card in self.get_all_installed_cards():
            if phase in card.effects:
                active_effects.append((card, card.effects[phase]))
        return active_effects


class Corp(Player):
    def __init__(self, deck: Deck, identity: Card):
        super().__init__(deck, identity)
        self.hq = Server("HQ", is_central=True)
        self.rd = Server("R&D", is_central=True)
        self.archives = Archives()
        self.remote_servers: List[Server] = []
        self.bad_publicity = 0

    def get_all_installed_cards(self):
        installed_cards = []
        for server in [self.hq, self.rd, self.archives] + self.remote_servers:
            installed_cards.extend(server.ice)
            installed_cards.extend(server.installed_cards)
        return installed_cards

    def __str__(self):
        return f"{super().__str__()}, Scored Area: {self.score_area}, Remote servers: {len(self.remote_servers)}"

    def take_action(self, game: Game):
        while self.clicks > 0:
            self.display_options(game)
            key = readchar.readkey()

            if key == "d":
                self.draw()
                self.clicks -= 1
            elif key == "c":
                self.gain_credits(1)
                self.clicks -= 1
            elif key == "p":
                if self.purge_virus_counters(game):
                    self.clicks -= 1
            elif key == "e":
                self.examine_servers()
            elif key == "a":
                if self.advance_card(game):
                    self.clicks -= 1
            elif key.isdigit() and 1 <= int(key) <= len(self.hand):
                game.handle_card_operation(self, self.hand[int(key) - 1])
            else:
                print("Invalid input. Try again.")
                continue

    def display_options(self, game):
        print(f"\nCorp's turn (Clicks: {
              self.clicks}, Credits: {self.credits}):")
        print("d: Draw a card")
        print("c: Gain 1 credit")
        print("p: Purge virus counters")
        print("e: Examine servers")
        print("a: Advance a card")
        print("t: Trash a resource if runner is tagged")
        print("q: End turn")
        game.display_hand(self)

    def install_card(self, game, card):
        if card.type == "ice":
            self.install_ice(game, card)
        elif card.type in ["asset", "upgrade", "agenda"]:
            self.install_in_server(game, card)
        else:
            print(f"Cannot install {card.type}")
            return False

        self.hand.remove(card)
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

    def install_in_server(self, game, card):
        servers = ["HQ", "R&D", "Archives"] + [
            f"Remote {i+1}" for i in range(len(self.remote_servers))
        ]
        servers.append("New Remote")

        for i, server in enumerate(servers):
            print(f"{i+1}: {server}")

        choice = int(input("Choose a server to install in: ")) - 1

        if choice == len(servers) - 1:
            self.remote_servers.append(Server(f"Remote {len(self.remote_servers) + 1}"))
            server = self.remote_servers[-1]
        elif choice < len(servers) - 1:
            server = self.get_server(servers[choice])
        else:
            print("Invalid choice")
            return

        server.install(card)
        print(f"{card.name} installed in {server.name}")

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
            self.archives.handle_card_discard(card)

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
            for card in server.installed_cards:
                if card.can_be_advanced():
                    advanceable_cards.append(card)
        return advanceable_cards

    def score_agenda(self, agenda, game):
        self.score_area.append(agenda)
        agenda.location.installed_cards.remove(agenda)
        print(f"Scored agenda: {agenda.name} worth {agenda.agenda_points} points.")
        game.check_win_condition()

    def rez_card(self, card: Card):
        if card.type in ["ice", "asset", "upgrade"] and not card.is_rezzed:
            if self.credits >= card.rez_cost:
                self.credits -= card.rez_cost
                card.rez()
                print(f"{card.name} has been rezzed")
            else:
                print(f"Not enough credits to rez {card.name}")
        else:
            print(f"Cannot rez {card.name}")

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
        # Remove virus counters from installed cards
        for card in self.corp.installed_cards + self.runner.installed_cards:
            if hasattr(card, "virus_counters"):
                card.virus_counters = 0

        # Remove virus counters from cards in servers
        for server in self.corp.remote_servers + [
            self.corp.hq,
            self.corp.rd,
            self.corp.archives,
        ]:
            for card in server.installed_cards:
                if hasattr(card, "virus_counters"):
                    card.virus_counters = 0

        # Trigger any "when virus counters are purged" effects
        self.effect_manager.trigger_virus_purge_effects()

        print("All virus counters have been purged.")

    def get_card_to_expose(self):
        # Implement logic to choose a card to expose
        # This could be from HQ, R&D, or installed cards
        pass

    def handle_card_discard(self, card: Card):
        self.archives.handle_card_discard(card)
        self.hand.remove(card)

    def examine_servers(self):
        while True:
            print("h: Examine HQ")
            print("r: Examine R&D")
            print("a: Examine Archives")
            print("q: Return")
            for i, server in enumerate(self.remote_servers, 1):
                print(f"{i}: Examine Remote Server {i}")
            key = readchar.readkey()
            if key == "h":
                self.hq.examine_server(self)
            elif key == "r":
                self.rd.examine_server(self)
            elif key == "a":
                self.archives.examine_server(self)
            elif key.isdigit() and 1 <= int(key) <= len(self.remote_servers):
                self.remote_servers[int(key) - 1].examine_server(self)
            elif key == "q":
                break


class Runner(Player):
    def __init__(self, deck: Deck, identity: Card):
        super().__init__(deck, identity)
        self.rig: Dict[str, List[Card]] = {
            "program": [],
            "hardware": [],
            "resource": [],
        }
        self.heap: List[Card] = []
        self.memory_units = 4
        self.link_strength = 0
        self.tags = 0

    def get_all_installed_cards(self):
        return self.rig["program"] + self.rig["hardware"] + self.rig["resource"]

    def __str__(self):
        return f"{super().__str__()}, {len(self.rig['program'])} programs, {len(self.rig['hardware'])} hardware, {len(self.rig['resource'])} resources"

    def install(self, card: Card):
        if card.type.lower() in self.rig:
            self.rig[card.type.lower()].append(card)

    def add_tag(self, amount):
        self.tags += amount
        print(f"{self.name} received {amount} tag{'s' if amount > 1 else ''}.")

    def remove_tag(self, count: int = 1):
        self.tags = max(0, self.tags - count)

    def take_action(self, game):
        while self.clicks > 0:
            self.display_options(game)
            key = readchar.readkey()

            if key == "d":
                self.draw()
            elif key == "c":
                self.gain_credits(1)
            elif key == "r":
                self.initiate_run(game)
            elif key == "t":
                self.remove_tag()
            elif key.isdigit() and 1 <= int(key) <= len(self.hand):
                self.handle_card_action(game, int(key) - 1)
            elif key == readchar.key.LEFT or key == readchar.key.RIGHT:
                # Handle cursor movement
                pass
            elif key == "q":
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
        game.display_hand(self)

    def use_icebreaker(self, icebreaker, ice):
        if icebreaker.can_interact(ice):
            cost = icebreaker.effects["persistent_ability"]["cost"]
            if self.can_pay(cost):
                self.pay(cost)

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

    def handle_card_discard(self, card: Card):
        self.heap.append(card)

    def get_installed_resources(self):
        return self.rig["resource"]

    def trash_resource(self, resource: Card):
        self.rig["resource"].remove(resource)
        self.heap.append(resource)
        print(f"{self.name}'s resource {resource.name} was trashed.")
