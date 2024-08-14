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

class Corp(Player):
    def __init__(self, deck: Deck, identity: Card):
        super().__init__(deck, identity)
        self.hq = Server("HQ", is_central=True)
        self.rd = Server("R&D", is_central=True)
        self.archives = Archives()
        self.remote_servers: List[Server] = []
        self.bad_publicity = 0

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
                self.purge_virus_counters()
                self.clicks -= 1
            elif key == "e":
                self.examine_servers()
            elif key.isdigit() and 1 <= int(key) <= len(self.hand):
                game.handle_card_operation(self, self.hand[int(key) - 1])
            else:
                print("Invalid input. Try again.")
                continue

    def display_options(self, game):
        print(f"\nCorp's turn (Clicks: {self.clicks}, Credits: {self.credits}):")
        print("d: Draw a card")
        print("c: Gain 1 credit")
        print("p: Purge virus counters")
        print("e: Examine servers")
        print("q: End turn")
        game.display_hand(self)

    def install_card(self, card):
        while True:
            server = input(
                f"Installing {card.name}, Choose a server to install, c to cancel (HQ/R&D/Archives/1/2/3/new...): "
            )
            if server.lower() in ["hq", "r&d", "archives", "new"] or server.isdigit():
                break
            elif server.lower() == "c":
                print("Installation canceled.")
                return
            else:
                print("Invalid server. Try again.")
        self.install_to_server(card, server)

    def rez_card(self, card):
        if self.can_pay(card.rez_cost):
            self.pay(card.rez_cost)
            card.is_rezzed = True
            self.game.handle_on_rez_effect(card)

    def install_to_server(self, card: Card, server: str):
        if server.lower() == "new":
            new_server = Server()
            new_server.handle_card_install(card)
            self.remote_servers.append(new_server)
        elif server.isdigit():
            server_index = int(server) - 1
            if 0 <= server_index < len(self.remote_servers):
                self.remote_servers[server_index].handle_card_install(card)
        elif server.lower() == "hq":
            self.hq.handle_card_install(card)
        # Add logic for installing in central servers if needed

    def forfeit_agenda(self, agenda):
        if agenda in self.score_area:
            self.score_area.remove(agenda)
            print(f"{self.name} forfeited {agenda.name}.")

    def add_bad_publicity(self, amount):
        self.bad_publicity += amount
        print(f"{self.name} gained {amount} bad publicity.")

    def get_card_to_expose(self):
        # Implement logic to choose a card to expose
        # This could be from HQ, R&D, or installed cards
        pass

    def handle_card_discard(self, card: Card):
        self.archives.handle_card_discard(card)

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
                self.hq.examine_server()
            elif key == "r":
                self.rd.examine_server()
            elif key == "a":
                self.archives.examine_server()
            elif key.isdigit() and 1 <= int(key) <= len(self.remote_servers):
                self.remote_servers[int(key) - 1].examine_server()
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
        print(f"\nRunner's turn (Clicks: {self.clicks}, Credits: {self.credits}):")
        print("d: Draw a card")
        print("c: Gain 1 credit")
        print("r: Initiate a run")
        print("t: Remove a tag")
        print("q: End turn")
        print("\nHand:")
        for i, card in enumerate(self.hand, 1):
            print(f"{i}: {card.name} ({card.type})")

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
