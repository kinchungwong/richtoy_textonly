from src.player_sys import Player
from src.board_sys import Board
from src.textio_sys import TextInputOutputBase
from src.minigames.minigame_base import MiniGameBase
from src.minihelps.ver0.list_owned_properties import ListOwnedProperties

class BankServices(MiniGameBase):
    player: Player
    board: Board

    def __init__(
        self,
        player: Player,
        board: Board,
        broadcast_io: TextInputOutputBase,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            player=player, 
            broadcast_io=broadcast_io, 
            player_io=player.textio,
            *args, 
            **kwargs,
        )
        self.player = player
        self.board = board

    def run(self) -> None:
        menu = [
            ("MS", "Mortgage Services", [
                lambda: self.run_mortgage(),
            ]),
            ("Q", "Quit / return to main menu", []),
        ]
        is_finished = False
        while not is_finished:
            choice_key = self.run_minigame_menu(menu)
            is_finished = choice_key in ("Q")
        return # def(run())

    def run_mortgage(self) -> None:
        menu = [
            ("LOP", "List Owned Properties", [
                lambda: self.run_list_owned_properties(),
            ]),
            ("MS", "Mortgage Services", [
                lambda: self.run_mortgage(),
            ]),
            ("Q", "Quit / return to main menu", []),
        ]
        is_finished = False
        while not is_finished:
            choice_key = self.run_minigame_menu(menu)
            is_finished = choice_key in ("Q")
        return # def(run_mortgage())

    def run_list_owned_properties(self) -> None:
        lop = ListOwnedProperties(
            player=self.player,
            board=self.board,
        )
        lop.show()
