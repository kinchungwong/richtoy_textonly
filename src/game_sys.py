from dataclasses import dataclass

from src.player_sys import Player
from src.walk_sys import WalkSession
from src.board_sys import BoardInfo, BoardStatus, Board

@dataclass(frozen=True)
class GameInfo:
    board_info: BoardInfo

@dataclass
class GameStatus:
    board_status: BoardStatus
    cur_round: int = 0
    cur_player: Player = None
    cur_walk: WalkSession = None

@dataclass(frozen=True)
class Game:
    info: GameInfo
    status: GameStatus

    def get_board(self) -> Board:
        return Board(
            info=self.info.board_info,
            status=self.status.board_status,
        )
