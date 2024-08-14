from typing import List
from ..cards.base import Card


class Server:
    def __init__(self, name: str, is_central: bool = False):
        self.name: str = name
        self.is_central: bool = is_central
        self.ice: List[Card] = []
        self.root: List[Card] = []
        self.upgrades: List[Card] = []

    def examine_server(self):
        print(f"Server: {self.name}")
        if self.ice:
            print("ICE:")
            for ice in self.ice:
                print(f"  {ice.name}")
        if self.root:
            print("Root:")
            for card in self.root:
                print(f"  {card.name}")
        if self.upgrades:
            print("Upgrades:")
            for upgrade in self.upgrades:
                print(f"  {upgrade.name}") 

    def handle_card_install(self, card: Card):
        if card.type == "ice":
            self.ice.append(card)
        elif card.type == "asset":
            if len(self.root) > 0:
                print("Cannot install assets in servers with installed cards.")
                return
            self.root.append(card)
        elif card.type == "upgrade":
            self.upgrades.append(card)
        elif card.type == "agenda":
            if self.is_central:
                print("Cannot install agendas in central servers.")
                return
            if len(self.root) > 0:
                print("Cannot install agendas in servers with installed cards.")
                return
            self.root.append(card)


class Archives(Server):
    def __init__(self):
        super().__init__("Archives", is_central=True)
        self.discard_pile = []

    def handle_card_discard(self, card: Card):
        self.discard_pile.append(card)

