from ..cards.base import Card
import src.players.player as Player


class Server:
    def __init__(self, name):
        self.name = name
        self.ice = []
        self.upgrades = []

    def install_ice(self, ice):
        self.ice.append(ice)

    def install_upgrade(self, upgrade):
        self.upgrades.append(upgrade)

    def examine_server(self, player):
        is_corp = isinstance(player, Player.Corp)

        print(f"\n{'=' * 40}")
        print(f"{self.name} Details".center(40))
        print(f"{'=' * 40}")

        self._print_ice(is_corp)
        self._print_upgrades(is_corp)
        self._print_server_specific_info(is_corp)

        input("\nPress Enter to return to server list...")

    def _print_ice(self, is_corp):
        print("\nICE (outermost to innermost):")
        if not self.ice:
            print("  No ICE installed")
        for i, ice in enumerate(self.ice):
            if is_corp or ice.is_rezzed:
                print(
                    f"  {i+1}. {ice.name} ({'Rezzed' if ice.is_rezzed else 'Unrezzed'})"
                )
                if ice.is_rezzed:
                    print(f"     Strength: {ice.strength}")
                    print("     Subroutines:")
                    for subroutine in ice.subroutines:
                        print(f"      [⊡] {subroutine}")
            else:
                print(f"  {i+1}. Unknown ICE (Unrezzed)")

    def _print_upgrades(self, is_corp):
        print("\nUpgrades:")
        if not self.upgrades:
            print("  No upgrades installed")
        for i, upgrade in enumerate(self.upgrades):
            if is_corp or upgrade.is_rezzed:
                print(
                    f"  {i+1}. {upgrade.name} ({'Rezzed' if upgrade.is_rezzed else 'Unrezzed'})"
                )
                if upgrade.is_rezzed:
                    print(f"     Trash cost: {upgrade.trash_cost}")
            else:
                print(f"  {i+1}. Unknown upgrade (Unrezzed)")

    def _print_server_specific_info(self, is_corp):
        # To be overridden by subclasses
        pass

    def get_card_status(self, card: Card) -> str:
        if card.type in ["ice", "asset", "upgrade"]:
            return "[Rezzed]" if card.is_rezzed else "[Unrezzed]"
        elif card.type == "agenda":
            return f"[Advancements: {card.advancement_tokens}]"
        else:
            return ""

    def get_card_info(self, card: Card) -> str:
        return f"{card.name} ({card.type})"


class RemoteServer(Server):
    def __init__(self, name):
        super().__init__(name)
        self.installed_card: Card = None  # Can be an asset or agenda

    def install_card(self, card):
        if self.installed_card:
            raise ValueError("This server already has an installed card")
        self.installed_card = card

    def _print_server_specific_info(self, is_corp):
        print("\nInstalled Card:")
        if self.installed_card:
            if is_corp or self.installed_card.is_rezzed:
                print(f"  {self.installed_card.name} ")
                if hasattr(self.installed_card, "is_rezzed"):
                    print(
                        f"({'Rezzed' if self.installed_card.is_rezzed else 'Unrezzed'})"
                    )
                if self.installed_card.is_rezzed:
                    if self.installed_card.type == "asset":
                        print(f"     Trash cost: {self.installed_card.trash_cost}")
                    elif self.installed_card.type == "agenda":
                        print(
                            f"     Advancement requirement: {self.installed_card.advancement_requirement}"
                        )
                        print(
                            f"     Agenda points: {self.installed_card.agenda_points}"
                        )
                        print(
                            f"     Current advancements: {self.installed_card.advancement_tokens}"
                        )
            else:
                print("  Unknown card (Unrezzed)")
        else:
            print("  No card installed")


class HQ(Server):
    def __init__(self):
        super().__init__("HQ")
        self.cards = []  # The Corp's hand

    def _print_server_specific_info(self, is_corp):
        if is_corp:
            print(f"\nCards in HQ: {len(self.cards)}")
            for i, card in enumerate(self.cards):
                print(f"  {i+1}. {card.name}")
        else:
            print(f"\nCards in HQ: {len(self.cards)} (inaccessible)")


class RD(Server):
    def __init__(self):
        super().__init__("R&D")
        self.cards = []  # This will be automatically updated by the Corp's deck property

    def _print_server_specific_info(self, is_corp):
        if is_corp:
            print(f"\nCards in R&D: {len(self.cards)}")
            print("Top 5 cards:")
            for i, card in enumerate(self.cards[:5]):
                print(f"  {i+1}. {card.name}")
        else:
            print(
                f"\nCards in R&D: {len(self.cards)} (top card accessible during runs)"
            )


class Archives(Server):
    def __init__(self):
        super().__init__("Archives")
        self.face_up_cards = []
        self.face_down_cards = []

    def handle_card_discard(self, card: Card, face_up=True):
        if face_up:
            self.face_up_cards.append(card)
        else:
            self.face_down_cards.append(card)
        card.location = self

    def _print_server_specific_info(self, is_corp):
        total_cards = len(self.face_up_cards) + len(self.face_down_cards)
        print(f"\nTotal cards in Archives: {total_cards}")
        print(f"Face-up cards: {len(self.face_up_cards)}")
        if is_corp:
            print(f"Face-down cards: {len(self.face_down_cards)}")
        if is_corp or self.face_up_cards:
            print("\nFace-up cards:")
            for card in self.face_up_cards:
                print(f"  - {card.name}")
