from src.textio_sys import TextInputOutputBase
from src.minigames.minigame_base import MiniGameBase
from src.minihelps.ver0.land_info import LandInfo

class LandPurchase(LandInfo, MiniGameBase):
    purchase_tx_complete: bool
    purchase_decline_tx_complete: bool

    def __init__(
        self,
        land_info: LandInfo,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            player=land_info.player, 
            square=land_info.square, 
            owner=land_info.owner, 
            broadcast_io=land_info.broadcast_io, 
            land_info=land_info, 
            player_io=land_info.player.textio,
            *args, 
            **kwargs,
        )
        self.purchase_tx_complete = False
        self.purchase_decline_tx_complete = False

    def run(self) -> None:
        self.land_purchase_offer_io()
        menu = [
            ("LI", "Land Info", [
                lambda: self.land_info_io(),
            ]),
            ("REI", "Rent Estimate Info", [
                lambda: self.rent_estimate_info_io(),
            ]),
            ("ALP", "Accept Land Purchase", [
                lambda: self.land_purchase_tx(),
                lambda: self.land_purchase_accepted_io(),
            ]),
            ("DLP", "Decline Land Purchase", [
                lambda: self.land_purchase_declined_tx(),
                lambda: self.land_purchase_declined_io(),
            ]),
        ]
        is_finished = False
        while not is_finished:
            choice_key = self.run_minigame_menu(menu)
            is_finished = choice_key in ("ALP", "DLP")
        return # def(run())

    def land_purchase_tx(self) -> None:
        assert self.can_purchase_now
        self.player.status.money -= self.land_value
        self.square.status.owner_index = self.player.info.index
        self.purchase_tx_complete = True

    def land_purchase_offer_io(self) -> None:
        assert self.can_purchase_now
        self.player_io.print(f"You can buy this land. Do you want to?")

    def land_purchase_accepted_io(self) -> None:
        assert self.can_purchase_now
        assert self.purchase_tx_complete
        # NOTE player_money has been updated to the new value
        self.player_io.print(f"I hear you say yes.")
        self.player_io.print(f"Square {self.location} is now yours.")
        self.player_io.print(f"You now have {self.player.status.money} dollars.")

    def land_purchase_declined_tx(self) -> None:
        assert self.can_purchase_now
        # NOTE future design, not implemented yet.
        if hasattr(self.player.status, "patience"):
            self.player.status.patience += 1
        self.purchase_decline_tx_complete = True
    
    def land_purchase_declined_io(self) -> None:
        assert self.can_purchase_now
        assert self.purchase_decline_tx_complete
        self.player_io.print(f"What a careful decision. May your wisdom grow each day.")
