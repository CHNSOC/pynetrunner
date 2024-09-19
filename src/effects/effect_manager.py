from __future__ import annotations
from ..game.gamephase import GamePhase

from typing import TYPE_CHECKING
import readchar

if TYPE_CHECKING:
    from ..game.game import Game
    from ..cards.base import Card
    from ..players.player import Player, Corp, Runner


class EffectManager:
    def __init__(self, game: Game):
        self.game = game

    def trigger_phase_effects(self, phase):
        if phase == GamePhase.CORP_TURN_BEGIN:
            self.handle_turn_start_effects(self.game.corp)
        elif phase == GamePhase.RUNNER_TURN_BEGIN:
            self.handle_turn_start_effects(self.game.runner)
        elif phase == GamePhase.CORP_TURN_END:
            self.game.corp.update_modifiers()
        elif phase == GamePhase.RUNNER_TURN_END:
            self.game.runner.update_modifiers()

    def trigger_virus_purge_effects(self):
        for card in (
            self.game.corp.get_all_installed_cards()
            + self.game.runner.get_all_installed_cards()
        ):
            if "on_virus_purge" in card.effects:
                self.handle_effect(card.effects["on_virus_purge"], card)

    def apply_persistent_effects(self, card: Card, player: Player):
        for effect in card.effects.get("persistent", []):
            if effect["type"] == "stat_modifier":
                player.add_modifier(card, effect["stat"], effect["amount"])

    def apply_effect(self, effect, card, player: Player):
        effect_type = effect["type"]

        if effect_type == "rez_ice_for_free":
            self.handle_rez_ice_for_free(card, player)
        elif effect_type == "draw_cards":
            player.draw(effect["amount"])
        elif effect_type == "gain_credits":
            player.gain_credits(effect["amount"])
        elif effect_type == "gain_bad_publicity":
            player.bad_publicity += 1
        elif effect_type == "run":
            self.game.run(player, effect["server"])
        elif effect_type == "increase_strength":
            card.strength += effect["amount"]
        elif effect_type == "break_subroutine":
            return True  # Implement subroutine breaking logic
        elif effect_type == "net_damage":
            self.game.runner.take_damage(effect["amount"], damage_type="net")
        elif effect_type == "take_credit":
            amount = effect.get("amount", 0)
            if card.hosted_counters >= amount:
                card.hosted_counters -= amount
                player.gain_credits(amount)
        elif effect_type == "place_credits":
            amount = effect.get("amount", 0)
            card.hosted_counters += amount
        elif effect_type == "on_transaction_play":
            if player.faction == "Weyland Consortium":
                player.gain_credits(1)
        elif effect_type == "search_and_install":
            self.handle_search_and_install(effect, card, player)
        elif effect_type == "increase_link_strength":
            player.add_modifier(card, "link", effect["amount"])

    def handle_card_install(self, card, player):
        self.handle_on_install_effects(card, player)
        self.apply_persistent_effects(card, player)

    def handle_on_install_effects(self, card: Card, player):
        effects = card.effects.get("on_install", [])
        for effect in effects:
            self.apply_effect(effect, card, player)

    def describe_effect(self, effect):
        if effect["type"] == "gain_credits":
            return f"Gain {effect['amount']} credits"
        elif effect["type"] == "expose_card":
            return (
                f"Expose {effect['amount']} card{'s' if effect['amount'] > 1 else ''}"
            )
        return "Unknown effect"

    def handle_player_choice(self, effect, card, player):
        choices = effect.get("choices", [])
        current_choice = 0

        while True:
            self.game.clear_screen()
            print(f"Choose an effect for {card.name}:")
            for i, choice in enumerate(choices):
                prefix = ">" if i == current_choice else " "
                print(f"{prefix} {self.describe_effect(choice)}")

            key = readchar.readkey()
            if key == readchar.key.UP and current_choice > 0:
                current_choice -= 1
            elif key == readchar.key.DOWN and current_choice < len(choices) - 1:
                current_choice += 1
            elif key == readchar.key.ENTER:
                chosen_effect = choices[current_choice]
                self.apply_effect(chosen_effect, card, player)
                break

    def handle_rez_ice_for_free(self, card, corp):
        unrezzed_ice = corp.get_all_unrezzed_ice()
        if not unrezzed_ice:
            print("There is no unrezzed ice to rez.")
            return

        print("Choose an ice to rez for free:")
        for i, ice in enumerate(unrezzed_ice):
            print(f"{i+1}. {ice.name} (normal rez cost: {ice.rez_cost})")

        choice = input("Enter the number of the ice you want to rez (or 0 to cancel): ")
        try:
            choice = int(choice)
            if 0 < choice <= len(unrezzed_ice):
                chosen_ice = unrezzed_ice[choice - 1]
                corp.rez_ice(chosen_ice, ignore_cost=True)
                print(f"{corp.name} rezzed {chosen_ice.name} for free!")
            elif choice != 0:
                print("Invalid choice. No ice was rezzed.")
        except ValueError:
            print("Invalid input. No ice was rezzed.")

    def handle_forfeit_choice(self, card, player):
        choice = input(
            f"Do you want to forfeit {card.name} to give the Runner 1 tag and take 1 bad publicity? (y/n): "
        )
        if choice.lower() == "y":
            pass  # TODO: Implement forfeit logic
            print(
                f"{player.name} forfeited {card.name}, gave the Runner 1 tag, and took 1 bad publicity."
            )
        else:
            print(f"{player.name} chose not to forfeit {card.name}.")

    def handle_expose_card(self, player, amount):
        for _ in range(amount):
            pass  # TODO: Implement card exposing logic

    def handle_on_play(self, card: Card, player: Player) -> None:
        effects = card.effects.get("on_play", [])
        for effect in effects:
            self.apply_effect(effect, card, player)

        if (
            card.type == "operation" and "transaction" in card.subtypes
        ):  # Need to expand this to handle other subtypes
            self.handle_identity_effects("on_transaction_play", player, card)

    def handle_turn_start_effects(self, player):
        active_cards = self.game.get_all_active_cards()
        for card in active_cards:
            if "on_turn_start" in card.effects:
                turn_Start_effects = card.effects.get("on_turn_start", [])
                for effect in turn_Start_effects:
                    self.apply_effect(effect, card, player)

    def handle_on_rez(self, card, player):
        effects = card.effects.get("on_rez", [])
        for effect in effects:
            self.apply_effect(effect, card, player)

    def handle_click_ability(self, card, player):
        effects = card.effects.get("click_ability", [])
        for effect in effects:
            if player.clicks >= effect["cost"]:
                player.clicks -= effect["cost"]
                self.apply_effect(effect, card, player)
                return True
        return False

    def handle_paid_ability(self, card, player, ability_index):
        abilities = card.effects.get("paid_abilities", [])
        if 0 <= ability_index < len(abilities):
            ability = abilities[ability_index]
            if player.credits >= ability["cost"]:
                player.credits -= ability["cost"]
                self.apply_effect(ability, card, player)

    def handle_identity_effects(self, trigger, player, *args, **kwargs):
        if trigger in player.identity.effects:
            for effect in player.identity.effects[trigger]:
                self.apply_effect(effect, player.identity, player)

    def handle_search_and_install(self, effect, card: Card, player: Corp | Runner):
        card_name = card.name
        if (
            self.game.user_input(
                f"Do you want to search for another copy of {card_name}? (y/n): ",
                ["y", "n"],
            )
            == "y"
        ):
            found_card = player.search_deck(card_name)
            if found_card and player.can_pay(found_card.cost):
                if (
                    self.game.user_input(
                        f"Install {card_name} for {found_card.cost} credits? (y/n): ",
                        ["y", "n"],
                    )
                    == "y"
                ):
                    player.spend_credits(found_card.cost)
                    player.deck.cards.remove(found_card)
                    player.install_card(self.game, found_card, prepaid=True)
                    player.shuffle_deck()
            else:
                print(f"No copy of {card_name} found or not enough credits to install.")
