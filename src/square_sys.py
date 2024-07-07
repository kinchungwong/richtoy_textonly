from dataclasses import dataclass

from src.player_sys import NOBODY

@dataclass(frozen=True)
class SquareInfo:
    location: int
    can_purchase: bool
    base_land_value: int

@dataclass
class SquareStatus:
    owner_index: int = NOBODY

@dataclass(frozen=True)
class Square:
    info: SquareInfo
    status: SquareStatus
