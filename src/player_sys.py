from dataclasses import dataclass

@dataclass(frozen=True)
class PlayerInfo:
    name: str
    index: int

@dataclass
class PlayerStatus:
    is_playing: bool = True
    in_prison: bool = False
    location: int = 0

@dataclass(frozen=True)
class Player:
    info: PlayerInfo
    status: PlayerStatus
