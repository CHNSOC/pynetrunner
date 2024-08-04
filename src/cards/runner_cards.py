
from .base import Card

class Program(Card):
    def __init__(self, name: str, cost: int, strength: int):
        super().__init__(name, cost, "Program")
        self.strength = strength


class Event(Card):
    def __init__(self, name: str, cost: int, effect):
        super().__init__(name, cost, "Event")
        self.effect = effect

class Operation(Card):
    def __init__(self, name: str, cost: int, effect):
        super().__init__(name, cost, "Operation")
        self.effect = effect

    def play(self, corp, game):
        if corp.credits >= self.cost:
            corp.credits -= self.cost
            corp.clicks -= 1
            self.effect(corp, game)
            corp.hand.remove(self)
            corp.archives.append(self)
            print(f"{corp.name} plays {self.name}")
            return True
        return False