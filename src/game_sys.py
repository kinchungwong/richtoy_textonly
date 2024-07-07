from dataclasses import dataclass

from src.player_sys import Player

@dataclass(frozen=True)
class GameInfo:
    pass

@dataclass
class GameStatus:
    cur_round: int = 0
    cur_player: Player = None

@dataclass(frozen=True)
class Game:
    info: GameInfo
    status: GameStatus
