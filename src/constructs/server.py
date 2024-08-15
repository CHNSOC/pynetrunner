from typing import List
from ..cards.base import Card
import src.players.player as Player


class Server:
    def __init__(self, name: str, is_central: bool = False):
        self.name: str = name
        self.is_central: bool = is_central
        self.ice: List[Card] = []
        self.installed_cards: List[Card] = []

    def install_ice(self, ice):
        self.ice.append(ice)

    def install(self, card: Card):
        if card.type == "upgrade":
            self.installed_cards.append(card)
            card.location = self
        elif len(self.installed_cards) == 0 or all(
            c.type == "upgrade" for c in self.installed_cards
        ):
            self.installed_cards.append(card)
            card.location = self
        else:
            raise ValueError("Cannot install in this server")

    def examine_server(self, player):
        print(f"\n=== {self.name} ===")

        # Display ICE
        if self.ice:
            print("ICE (outermost to innermost):")
            for i, ice in enumerate(self.ice, 1):
                status = self.get_card_status(ice)
                print(f"  {i}. {ice.name:<20} {status}")
        else:
            print("No ICE installed")

        print("\nInstalled cards:")

        # Display installed cards
        if self.installed_cards:
            for i, card in enumerate(self.installed_cards, 1):
                status = self.get_card_status(card)
                card_info = self.get_card_info(card)
                print(f"  {i}. {card_info:<20} {status}")
        else:
            print("  No cards installed")

        print("\n" + "=" * (len(self.name) + 8))

    def get_card_status(self, card: Card) -> str:
        if card.type in ["ice", "asset", "upgrade"]:
            return "[Rezzed]" if card.is_rezzed else "[Unrezzed]"
        elif card.type == "agenda":
            return f"[Advancements: {card.advancement_tokens}]"
        else:
            return ""

    def get_card_info(self, card: Card) -> str:
        return f"{card.name} ({card.type})"


class Archives(Server):
    def __init__(self):
        super().__init__("Archives", is_central=True)
        self.discard_pile = []

    def handle_card_discard(self, card: Card):
        self.discard_pile.append(card)
