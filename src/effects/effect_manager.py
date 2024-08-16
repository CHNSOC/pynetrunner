class EffectManager:
    def __init__(self, game):
        self.game = game
        self.global_effects = []

    def handle_on_play(self, card, player):
        effects = card.effects.get("on_play", [])
        for effect in effects:
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

    def handle_paid_ability(self, card, player, ability_index):
        abilities = card.effects.get("paid_abilities", [])
        if 0 <= ability_index < len(abilities):
            ability = abilities[ability_index]
            if player.credits >= ability["cost"]:
                player.credits -= ability["cost"]
                self.apply_effect(ability, card, player)

    def add_global_effect(self, effect):
        self.global_effects.append(effect)

    def trigger_global_effects(self, trigger, **kwargs):
        for effect in self.global_effects:
            if effect.trigger == trigger:
                effect.action(self.game, **kwargs)

    def trigger_virus_purge_effects(self):
        for card in (
            self.game.corp.get_all_installed_cards()
            + self.game.runner.get_all_installed_cards()
        ):
            if "on_virus_purge" in card.effects:
                self.handle_effect(card.effects["on_virus_purge"], card)

    def apply_effect(self, effect, card, player):
        effect_type = effect["type"]

        if effect_type == "rez_ice_for_free":
            self.handle_rez_ice_for_free(card, player)
        elif effect_type == "draw_cards":
            player.draw(effect["amount"])
        elif effect_type == "gain_credits":
            player.gain_credits(effect["amount"])
        elif effect_type == "run":
            self.game.run(player, effect["server"])
        elif effect_type == "increase_strength":
            card.strength += effect["amount"]
        elif effect_type == "break_subroutine":
            return True  # Implement subroutine breaking logic
        elif effect_type == "net_damage":
            self.game.runner.take_damage(effect["amount"], damage_type="net")
        elif effect_type == "gain_credits_on_transaction":
            if card.type == "operation" and "transaction" in card.subtypes:
                player.gain_credits(effect["amount"])
        # Add more effect types as needed

    def handle_player_choice(self, effect, card, player):
        choices = effect.get("choices", [])
        print(f"Choose an effect for {card.name}:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {self.describe_effect(choice)}")

        while True:
            try:
                choice_index = int(input("Enter your choice (number): ")) - 1
                if 0 <= choice_index < len(choices):
                    chosen_effect = choices[choice_index]
                    self.apply_effect(chosen_effect, card, player)
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")

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

    def describe_effect(self, effect):
        effect_type = effect.get("type")
        amount = effect.get("amount", 0)
        if effect_type == "gain_credits":
            return f"Gain {amount} credits"
        elif effect_type == "expose_card":
            return f"Expose {amount} card{'s' if amount > 1 else ''}"
        return "Unknown effect"

    def handle_persistent_effects(self, player):
        for card in player.installed_cards:
            effects = card.effects.get("persistent", [])
            for effect in effects:
                self.apply_persistent_effect(effect, card, player)

    def apply_persistent_effect(self, effect, card, player):
        self.apply_effect(effect, card, player)

    def handle_effect(self, effect, card):
        effect_type = effect.get("type")
        if effect_type == "draw":
            self.game.current_player.draw(effect.get("amount", 1))
        elif effect_type == "gain_credits":
            self.game.current_player.gain_credits(effect.get("amount", 1))


class GlobalEffect:
    def __init__(self, trigger, action):
        self.trigger = trigger
        self.action = action


class AgendaScoredOrStolenEffect(GlobalEffect):
    def __init__(self):
        super().__init__(
            trigger="agenda_scored_or_stolen",
            effect={"type": "net_damage", "amount": 1},
        )
