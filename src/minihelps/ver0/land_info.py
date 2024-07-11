import inspect
from typing import Optional

from src.textio_sys import TextInputOutputBase
from src.player_sys import Player, NOBODY
from src.square_sys import Square
from src.minihelps.minihelp_base import MiniHelpBase
from src.minihelps.ver0.square_info import SquareInfo

class LandInfo(SquareInfo):
    player: Player
    player_io: TextInputOutputBase
    square: Square
    owner: Optional[Player]
    owner_is_player: bool
    owner_name: Optional[str]
    owner_io: Optional[TextInputOutputBase]
    land_value: int
    land_rent: int
    can_purchase_now: bool
    need_pay_rent: bool
    can_pay_rent_now: bool
    will_go_to_prison: bool
    broadcast_io: TextInputOutputBase

    @staticmethod
    def check_init_preconditions(
        player: Player,
        square: Square,
        owner: Optional[Player],
        broadcast_io: TextInputOutputBase,
        *args,
        **kwargs,
    ) -> bool:
        return square.info.can_purchase

    @staticmethod
    def check_init_preconditions_and_raise(*args, **kwargs) -> None:
        precond_fn = __class__.check_init_preconditions
        if not precond_fn(*args, **kwargs):
            precond_fn_pysrc = inspect.getsource(precond_fn)
            raise Exception(precond_fn_pysrc)

    def __init__(
        self,
        player: Player,
        square: Square,
        owner: Optional[Player],
        broadcast_io: TextInputOutputBase,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(square=square)
        __class__.check_init_preconditions_and_raise(
            player,
            square,
            owner,
            broadcast_io,
            *args,
            **kwargs,
        )
        self.player = player
        self.player_io = player.textio
        self.owner = owner
        self.owner_is_player = owner is not None and (owner.info.index == player.info.index)
        self.owner_name = owner.info.name if owner is not None else None
        self.owner_io = owner.textio if owner is not None else None
        self.land_value = square.get_land_value()
        self.land_rent = square.get_rent()
        self.can_purchase_now = owner is None and (player.status.money >= self.land_value)
        self.need_pay_rent = owner is not None and not self.owner_is_player and not owner.status.in_prison
        self.can_pay_rent_now = self.need_pay_rent and (player.status.money >= self.land_value)
        self.will_go_to_prison = self.need_pay_rent and not self.can_pay_rent_now
        self.broadcast_io = broadcast_io

    def land_info_io(self):
        self.player_io.print(f"This land can be purchased and isn't owned yet.")
        self.player_io.print(f"Its current land value is {self.land_value}.")
        self.player_io.print(f"You have {self.player.status.money} dollars.")

    def rent_estimate_info_io(self):
        self.player_io.print("Based on current estimates, it would generate:")
        self.player_io.print(f"... {self.land_rent} per turn, if not visited, and")
        self.player_io.print(f"... {self.land_rent * 10} per turn, if visited by another player.")
