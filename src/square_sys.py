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
    additive_land_value: int = 0
    additive_popularity: int = 0

@dataclass(frozen=True)
class Square:
    info: SquareInfo
    status: SquareStatus

    def get_land_value(self) -> int:
        base_value = self.info.base_land_value
        add_value = self.status.additive_land_value
        percent = 100 + self.status.additive_popularity
        return ((base_value + add_value) * percent) // 100

    def get_mortgage_value(self) -> int:
        # Mortgage value disregards development and popularity.
        base_value = self.info.base_land_value
        return base_value // 2

    def get_rent(self) -> int:
        return max(1, self.get_land_value() // 10)
