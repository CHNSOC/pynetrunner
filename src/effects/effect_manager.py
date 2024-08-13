class EffectManager:
    def __init__(self, game):
        self.game = game
        self.global_effects = []

    def handle_on_play(self, card, player):
        effects = card.effects.get('on_play', [])
        for effect in effects:
            self.apply_effect(effect, card, player)

    def handle_click_ability(self, card, player):
        effects = card.effects.get('click_ability', [])
        for effect in effects:
            if player.clicks >= effect['cost']:
                player.clicks -= effect['cost']
                self.apply_effect(effect, card, player)

    def handle_paid_ability(self, card, player, ability_index):
        abilities = card.effects.get('paid_abilities', [])
        if 0 <= ability_index < len(abilities):
            ability = abilities[ability_index]
            if player.credits >= ability['cost']:
                player.credits -= ability['cost']
                self.apply_effect(ability, card, player)

    def add_global_effect(self, effect):
        self.global_effects.append(effect)

    def trigger_global_effects(self, trigger, **kwargs):
        for effect in self.global_effects:
            if effect.trigger == trigger:
                effect.action(self.game, **kwargs)

    def apply_effect(self, effect, card, player):
        effect_type = effect['type']
        if effect_type == 'draw_cards':
            player.draw(effect['amount'])
        elif effect_type == 'gain_credits':
            player.gain_credits(effect['amount'])
        elif effect_type == 'run':
            self.game.run(player, effect['server'])
        elif effect_type == 'increase_strength':
            card.strength += effect['amount']
        elif effect_type == 'break_subroutine':
            return True  # Implement subroutine breaking logic
        elif effect_type == 'net_damage':
            self.game.runner.take_damage(effect['amount'], damage_type="net")
        elif effect_type == 'gain_credits_on_transaction':
            if card.type == 'operation' and 'transaction' in card.subtypes:
                player.gain_credits(effect['amount'])
        # Add more effect types as needed

    def handle_persistent_effects(self, player):
        for card in player.installed_cards:
            effects = card.effects.get('persistent', [])
            for effect in effects:
                self.apply_persistent_effect(effect, card, player)

    def apply_persistent_effect(self, effect, card, player):
        self.apply_effect(effect, card, player)


class GlobalEffect:
    def __init__(self, trigger, action):
        self.trigger = trigger
        self.action = action


class AgendaScoredOrStolenEffect(GlobalEffect):
    def __init__(self):
        super().__init__(
            trigger="agenda_scored_or_stolen",
            effect={'type': 'net_damage', 'amount': 1}
        )
