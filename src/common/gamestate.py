from enum import Enum

class PlayerType(Enum):
    CORP = "Corporation"
    RUNNER = "Runner"

class GameState:
    def __init__(self):
        self.current_player = None
        self.turn_number = 0
        self.current_phase = None
        self.corp_score = 0
        self.runner_score = 0

game_state = GameState()