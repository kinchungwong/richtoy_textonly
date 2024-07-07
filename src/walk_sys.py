from dataclasses import dataclass

@dataclass(frozen=True)
class WalkInfo:
    game_round: int
    player_index: int
    move_points: int

@dataclass()
class WalkStatus:
    move_points_used: int = 0

@dataclass(frozen=True)
class WalkSession:
    info: WalkInfo
    status: WalkStatus
