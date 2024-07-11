import inspect
from typing import Optional

from src.textio_sys import TextInputOutputBase
from src.player_sys import Player, NOBODY
from src.square_sys import Square
from src.board_sys import Board
from src.minihelps.minihelp_base import MiniHelpBase

class ListOwnedProperties(MiniHelpBase):
    player: Player
    board: Board

    def __init__(
        self,
        player: Player,
        board: Board, 
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.player = player
        self.board = board

    def show(self) -> None:
        player = self.player
        player_io = self.player.textio
        board = self.board
        for location in board.enumerate_locations():
            square = board.get_square(location)
            if square.status.owner_index != player.info.index:
                continue
            land_value = square.get_land_value()
            mortgage_value = square.get_mortgage_value()
            s_location = str(location).rjust(3)
            s_land_value = str(land_value).rjust(4)
            s_mortgage_value = str(mortgage_value).rjust(4)
            player_io.print(f"Location {s_location} : land value {s_land_value}, mortgage value: {s_mortgage_value}")
