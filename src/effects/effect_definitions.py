
from ..cards.card_effects import CardEffect

def register_card_effects(registry):
    # Adonis Campaign
    registry.register_effect(CardEffect(
        card_id="adonis_campaign",
        condition=lambda game, card: card.is_rezzed(),
        action=lambda game, card: game.corp.gain_credits(3)
    ))

    # Magnum Opus
    registry.register_effect(CardEffect(
        card_id="magnum_opus",
        condition=lambda game, card: game.runner.clicks > 0,
        action=lambda game, card: (game.runner.gain_credits(2), game.runner.spend_click())
    ))
