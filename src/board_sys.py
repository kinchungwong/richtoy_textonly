from dataclasses import dataclass

from src.square_sys import SquareInfo, SquareStatus, Square

@dataclass(frozen=True)
class BoardInfo:
    squares_info: tuple[SquareInfo, ...]
    pass

@dataclass
class BoardStatus:
    squares_status: list[SquareStatus]

@dataclass(frozen=True)
class Board:
    info: BoardInfo
    status: BoardStatus

    def get_square(self, location: int) -> Square:
        return Square(
            self.info.squares_info[location],
            self.status.squares_status[location],
        )
