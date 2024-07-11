from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias

from src.square_sys import SquareInfo, SquareStatus, Square

Location = int

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

    def enumerate_locations(self) -> Iterable[Location]:
        # Subject to change, and not necessarily a big circle.
        # (City street grids are not circles.)
        count = len(self.info.squares_info)
        for location in range(count):
            yield location

    def get_square(self, location: int) -> Square:
        return Square(
            self.info.squares_info[location],
            self.status.squares_status[location],
        )
