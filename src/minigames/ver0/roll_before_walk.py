import random
from typing import Optional

from src.player_sys import Player
from src.board_sys import Board
from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.textio_sys import TextInputOutputBase
from src.minigames.minigame_base import MiniGameBase
from src.minigames.ver0.bank_services import BankServices

class RollBeforeWalk(MiniGameBase):
    game_round: int
    board: Board
    player: Player
    broadcast_io: TextInputOutputBase
    dice_roll_result: tuple[int, int]
    walk_session: Optional[WalkSession]

    def __init__(
        self,
        game_round: int, 
        player: Player,
        board: Board,
        broadcast_io: TextInputOutputBase,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            player=player, 
            board=board,
            broadcast_io=broadcast_io, 
            player_io=player.textio,
            *args, 
            **kwargs,
        )
        self.game_round = game_round
        self.player = player
        self.board = board
        self.broadcast_io = broadcast_io
        self.dice_roll_result = (-1, -1)
        self.walk_session = None

    def run(self) -> None:
        self.before_roll_io()
        menu = [
            ("RTD", "Roll The Dice", [
                lambda: self.roll_the_dice_local(),
                lambda: self.after_roll_local(),
                lambda: self.after_roll_io(),

            ]),
            ("BS", "Bank Services", [
                lambda: self.delegate_bank_services(),
            ]),
        ]
        is_finished = False
        while not is_finished:
            choice_key = self.run_minigame_menu(menu)
            is_finished = choice_key in ("RTD")
        return # def(run())

    def before_roll_io(self) -> None:
        name = self.player.info.name
        self.player_io.print(f"Player {name}, please roll the dice.")

    def roll_the_dice_local(self) -> None:
        self.dice_roll_result = (
            random.randint(1, 6),
            random.randint(1, 6),
        )

    def after_roll_io(self) -> None:
        name = self.player.info.name
        dice_0, dice_1 = self.dice_roll_result
        move_points = dice_0 + dice_1
        self.player_io.print(f"{name}, you rolled {dice_0}, {dice_1}, so you will walk {move_points} squares.")

    def after_roll_local(self) -> None:
        move_points = sum(self.dice_roll_result)
        self.walk_session = WalkSession(
            info=WalkInfo(
                game_round=self.game_round,
                player_index=self.player.info.index,
                move_points=move_points,
            ),
            status=WalkStatus(),
        )

    def delegate_bank_services(self) -> None:
        bs = BankServices(
            player=self.player,
            board=self.board,
            broadcast_io=self.broadcast_io,
        )
        bs.run()
