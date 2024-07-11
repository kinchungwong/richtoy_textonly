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

    def run(self):
        self.rent_info_io()
        if self.can_pay_rent_now:
            self.pay_rent_tx()
            self.rent_pay_success_io()
        elif self.will_go_to_prison:
            self.go_to_prison_tx()
            self.rent_pay_failure_io()

    def rent_info_io(self):
        assert self.owner is not None
        assert not self.owner_is_player
        assert self.need_pay_rent
        self.player_io.print(f"This land is owned by {self.owner_name}.")
        self.player_io.print(f"You must pay rent, which is {self.land_rent}.")

    def pay_rent_tx(self):
        assert self.can_pay_rent_now
        self.player.status.money -= self.land_rent
        self.owner.status.money += self.land_rent

    def go_to_prison_tx(self):
        assert self.will_go_to_prison
        self.player.status.in_prison = True

    def rent_pay_success_io(self):
        assert self.owner is not None
        assert not self.owner_is_player
        assert self.need_pay_rent
        assert self.can_pay_rent_now
        self.player_io.print(f"You now have {self.player.status.money} dollars.")
        self.owner_io.print(f"Player {self.player.info.name} has paid you {self.land_rent} dollars of rent.")

    def rent_pay_failure_io(self):
        assert self.owner is not None
        assert not self.owner_is_player
        assert self.need_pay_rent
        assert not self.can_pay_rent_now
        assert self.will_go_to_prison
        self.player_io.print(f"Unfortunately, you don't have the money to pay rent, therefore you are now in prison.")
        self.owner_io.print(f"Player {self.player.info.name} was unable to pay the rent of {self.land_rent} dollars, and was sent to prison.")
