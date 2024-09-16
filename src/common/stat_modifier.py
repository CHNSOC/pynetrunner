
class StatModifier:
    def __init__(self, source, stat, amount):
        self.source = source
        self.stat = stat
        self.amount = amount

class TemporaryModifier(StatModifier):
    def __init__(self, source, stat, amount, duration):
        super().__init__(source, stat, amount)
        self.duration = duration
