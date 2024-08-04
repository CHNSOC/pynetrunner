from .base import Card

class ICE(Card):
    def __init__(self, name: str, cost: int, strength: int):
        super().__init__(name, cost, "ICE")
        self.strength = strength
        self.rezzed = False

    def rez(self, corp):
        if not self.rezzed and corp.credits >= self.cost:
            corp.credits -= self.cost
            self.rezzed = True
            print(f"{corp.name} rezzes {self.name}")
            return True
        return False

class Agenda(Card):
    def __init__(self, name: str, cost: int, agenda_points: int):
        super().__init__(name, cost, "Agenda")
        self.agenda_points = agenda_points

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