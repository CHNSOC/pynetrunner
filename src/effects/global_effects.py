class GlobalEffect:
    def __init__(self, trigger, action):
        self.trigger = trigger
        self.action = action

class AgendaScoredOrStolenEffect(GlobalEffect):
    def __init__(self):
        super().__init__(
            trigger="agenda_scored_or_stolen",
            action=self.do_net_damage
        )

    def do_net_damage(self, game):
        game.runner.take_damage(1, damage_type="net")
        print(f"{game.corp.name}'s identity inflicts 1 net damage!")