import random
from typing import Optional

from src.player_sys import Player
from src.board_sys import Board
from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.textio_sys import TextInputOutputBase
from src.minigames.minigame_base import MiniGameBase

Location = int

class InsidePrison(MiniGameBase):
    PRISON_EXIT_INITIAL_LOCATION: Location = 0
    player: Player
    dice_roll_result: Optional[tuple[int, int]]
    broadcast_io: TextInputOutputBase
    can_get_out_of_prison: bool

    def __init__(
        self,
        player: Player,
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
        self.broadcast_io = broadcast_io
        self.dice_roll_result = None
        self.can_get_out_of_prison = False

    def run(self) -> None:
        self.before_roll_bio()
        self.before_roll_io()
        menu = [
            ("RTD", "Roll The Dice", [
                lambda: self.roll_the_dice_local(),
                lambda: self.after_roll_io(),
                lambda: self.after_roll_tx(),
            ]),
        ]
        is_finished = False
        while not is_finished:
            choice_key = self.run_minigame_menu(menu)
            is_finished = choice_key in ("RTD")
        return # def(run())

    def before_roll_bio(self) -> None:
        name = self.player.info.name
        self.broadcast_io.print(f"Player {name} was in prison.")

    def before_roll_io(self) -> None:
        name = self.player.info.name
        self.player_io.print(f"{name}, please roll the dice. If you roll a double, you can get out of prison.")

    def roll_the_dice_local(self) -> None:
        self.dice_roll_result = (
            random.randint(1, 6),
            random.randint(1, 6),
        )

    def after_roll_io(self) -> None:
        assert self.dice_roll_result is not None
        name = self.player.info.name
        dice_0, dice_1 = self.dice_roll_result
        self.player_io.print(f"{name}, you rolled {dice_0}, {dice_1}.")
        self.can_get_out_of_prison = (dice_0 == dice_1)
        if self.can_get_out_of_prison:
            exit_location = self.PRISON_EXIT_INITIAL_LOCATION
            self.player_io.print(f"Because you rolled a double, you can now get out of prison, and will start at square {exit_location}.")
        else:
            self.player_io.print(f"Because you did not roll a double, you will remain in prison.")

    def after_roll_tx(self) -> None:
        assert self.dice_roll_result is not None
        if self.can_get_out_of_prison:
            self.player.status.in_prison = False
            self.player.status.location = self.PRISON_EXIT_INITIAL_LOCATION
