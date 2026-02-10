from enum import Enum, auto


class FBStates(Enum):
    RUNNING = 0
    IDLE = auto()
    STOPPED = auto()
    KILLED = auto()


class ManagerCommandType(Enum):
    START = auto()
    STOP = auto()
    KILL = auto()
    RESET = auto()
