

class CardEffect:
    def __init__(self, card_id, phase, condition=None, action=None):
        self.card_id = card_id
        self.phase = phase
        self.condition = condition or (lambda game, card: True)
        self.action = action or (lambda game, card: None)

    def apply(self, game, card):
        if self.condition(game, card):
            self.action(game, card)
