class Card:
    def __init__(self, name: str, cost: int, card_type: str):
        self.name = name
        self.cost = cost
        self.type = card_type

    def play(self, player, game):
        pass

    
def gain_credits(amount):
    def effect(player, game):
        player.credits += amount
        print(f"{player.name} gains {amount} credits")
    return effect


def draw_cards(amount):
    def effect(player, game):
        player.draw(amount)
        print(f"{player.name} draws {amount} cards")
    return effect