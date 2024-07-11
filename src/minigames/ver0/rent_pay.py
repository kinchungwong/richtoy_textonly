import builtins

from src.minigames.minigame_base import MiniGameBase
from src.minihelps.ver0.land_info import LandInfo

class RentPay(LandInfo, MiniGameBase):
    def __init__(
        src, 
        land_info: LandInfo,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **(builtins.vars(land_info) | kwargs))

    def rent_info_io(self):
        assert self.owner is not None
        assert not self.owner_is_player
        assert self.need_pay_rent
        self.player_io.print(f"This land is owned by {self.owner_name}.")
        self.player_io.print(f"You must pay rent, which is {self.land_rent}.")
