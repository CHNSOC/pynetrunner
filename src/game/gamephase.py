from enum import Enum, auto


class GamePhase(Enum):
    CORP_TURN_BEGIN = auto()
    CORP_DRAW = auto()
    CORP_ACTION = auto()
    CORP_DISCARD = auto()
    CORP_TURN_END = auto()
    RUNNER_TURN_BEGIN = auto()
    RUNNER_ACTION = auto()
    RUNNER_DISCARD = auto()
    RUNNER_TURN_END = auto()
    RUN_INITIATION = auto()
    RUN_APPROACH_ICE = auto()
    RUN_ENCOUNTER_ICE = auto()
    RUN_PASS_ICE = auto()
    RUN_APPROACH_SERVER = auto()
    RUN_SUCCESS = auto()
    RUN_END = auto()