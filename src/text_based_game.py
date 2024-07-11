import builtins
import random
from typing import NamedTuple, Any, Literal, Optional
from dataclasses import dataclass


from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.player_sys import PlayerInfo, PlayerStatus, Player, NOBODY
from src.board_sys import BoardInfo, BoardStatus, Board
from src.square_sys import SquareInfo, SquareStatus, Square
from src.game_sys import GameInfo, GameStatus, Game
from src.textio_sys import DefaultTextInputOutput, BroadcastTextInputOutput
from src.textio_agent_sys import AgentHistoryTextInputOutput, TextInputOutputHistory

class Mini:
    from src.minihelps.ver0.square_info import SquareInfo
    from src.minihelps.ver0.land_info import LandInfo
    from src.minigames.ver0.land_purchase import LandPurchase
    from src.minigames.ver0.rent_pay import RentPay
    from src.minigames.ver0.roll_before_walk import RollBeforeWalk
    from src.minigames.ver0.inside_prison import InsidePrison

mini = Mini()

class TextBasedGame:
    NUM_SQUARES: Literal[100] = 100
    game: Game
    players: list[Player]
    broadcast: BroadcastTextInputOutput ### TODO rename to "broadcast_io"

    def __init__(self) -> None:
        board_info, board_status = self.create_board()
        self.game = Game(
            info=GameInfo(
                board_info=board_info,
            ),
            status=GameStatus(
                board_status=board_status,
            ),
        )
        self.players = []
        self.broadcast = BroadcastTextInputOutput()

    def init_squares(self) -> list[tuple[SquareInfo, SquareStatus]]:
        squares: list[tuple[SquareInfo, SquareStatus]] = []
        for location in range(self.NUM_SQUARES):
            can_purchase = ((location % 10) != 0)
            base_land_value = random.randint(10, 20) if can_purchase else 0
            sqinfo = SquareInfo(
                location=location,
                can_purchase=can_purchase,
                base_land_value=base_land_value,
            )
            sqsts = SquareStatus()
            squares.append((sqinfo, sqsts))
        return squares
    
    def create_board(self) -> tuple[BoardInfo, BoardStatus]:
        squares = self.init_squares()
        board_info = BoardInfo(
            squares_info=tuple(sqinfo for sqinfo, _ in squares),
        )
        board_status = BoardStatus(
            squares_status=list(sqsts for _, sqsts in squares),
        )
        return board_info, board_status

    def add_player(self, detail: dict[str, Any]) -> int:
        assert type(detail) == dict
        detail = detail.copy()
        index = len(self.players)
        detail["index"] = index
        player = self._create_player_instance(detail)
        self.players.append(player)
        self.broadcast.add(player.textio)

    def _create_player_instance(self, detail: dict[str, Any]) -> Player:
        assert type(detail) == dict
        info_kw_list = set(["name", "index"])
        status_kw_list = set([])
        player_kw_list = set(["textio"])
        info_detail = { k:v for k, v in detail.items() if k in info_kw_list }
        status_detail = { k:v for k, v in detail.items() if k in status_kw_list }
        player_detail = { k:v for k, v in detail.items() if k in player_kw_list }
        return Player(
            info=PlayerInfo(**info_detail),
            status=PlayerStatus(**status_detail),
            **player_detail,
        )

    def run_main(self):
        should_continue = True
        while should_continue:
            should_continue = self.run_single_round()
        self.summarize_endgame()

    def run_single_round(self) -> bool:
        if not self.is_game_playing():
            return False
        self.run_all_player_turns()
        if not self.is_game_playing():
            return False
        self.game.status.cur_round += 1
        return True

    def run_all_player_turns(self):
        player_count = len(self.players)
        for player_index in range(player_count):
            self.game.status.cur_player = self.players[player_index]
            self.run_player_turn()

    def run_player_turn(self):
        cur_round = self.game.status.cur_round
        player = self.game.status.cur_player
        if not player.status.is_playing:
            return
        player.textio.print(f"round {(cur_round)}, player {(player.info.index)}, name {player.info.name}")
        if player.status.in_prison:
            self.run_player_prison_turn()
        else:
            self.run_player_normal_turn()

    def run_player_prison_turn(self):
        player = self.game.status.cur_player
        inside_prison = mini.InsidePrison(
            player=player, 
            broadcast_io=self.broadcast,
        )
        inside_prison.run()

    def run_player_normal_turn(self):
        self.game.status.cur_walk = self.roll_the_dice()
        while not self.is_walk_finished():
            self.walk_single_step()
        self.on_walk_finished()
        self.game.status.cur_walk = None

    def roll_the_dice(self) -> WalkSession:
        game_round = self.game.status.cur_round
        player = self.game.status.cur_player
        roll_before_walk = mini.RollBeforeWalk(
            game_round=game_round,
            player=player,
            board=self.game.get_board(),
            broadcast_io=self.broadcast,
        )
        roll_before_walk.run()
        walk_session = roll_before_walk.walk_session
        return walk_session

    def walk_single_step(self):
        if self.is_walk_finished():
            return
        gsts = self.game.status
        walk = gsts.cur_walk
        winfo = walk.info
        wsts = walk.status
        wsts.move_points_used += 1
        player = self.game.status.cur_player
        pinfo = player.info
        psts = player.status
        psts.location = (psts.location + 1) % self.NUM_SQUARES

    def on_walk_finished(self):
        player = self.game.status.cur_player
        square = self.get_square(player.status.location)
        owner = self.get_owner(square)
        square_info = mini.SquareInfo(square)
        if square_info.can_purchase:
            land_info = mini.LandInfo(player=player, square=square, owner=owner, broadcast_io=self.broadcast)
            if land_info.can_purchase_now:
                land_purchase = mini.LandPurchase(land_info=land_info)
                land_purchase.run()
            elif land_info.need_pay_rent:
                rent_pay = mini.RentPay(land_info=land_info, player=player, square=square, owner=owner, broadcast_io=self.broadcast)
                rent_pay.run()
            else:
                pass

    def get_square(self, location: int) -> Square:
        return self.game.get_board().get_square(location)

    def get_owner(self, square: Square) -> Optional[Player]:
        owner_index = square.status.owner_index
        if 0 <= owner_index < len(self.players):
            return self.players[owner_index]
        return None

    def is_game_playing(self) -> bool:
        num_playing = 0
        for player in self.players:
            if player.status.is_playing and not player.status.in_prison:
                num_playing += 1
                if num_playing >= 2:
                    return True
        return False

    def summarize_endgame(self):
        total_players = len(self.players)
        num_quit = 0
        num_in_prison = 0
        players_active: list[Player] = []
        for player in self.players:
            if not player.status.is_playing:
                num_quit += 1
            elif player.status.in_prison:
                num_in_prison += 1
            else:
                players_active.append(player)
        if num_quit == total_players:
            self.broadcast.print("Game ended. All players have quit.")
        elif num_in_prison == total_players:
            self.broadcast.print("Game ended. All players are in prison.")
        elif len(players_active) == 1:
            winner = players_active[0]
            winner_name = winner.info.name
            money = winner.status.money
            self.broadcast.print(f"Game is won by {winner_name}, with {money} dollars at the end.")

    def is_walk_finished(self) -> bool:
        gsts = self.game.status
        walk = gsts.cur_walk
        if walk is None:
            return True
        winfo = walk.info
        wsts = walk.status
        return wsts.move_points_used == winfo.move_points

if __name__ == "__main__":
    game = TextBasedGame()
    textio = DefaultTextInputOutput()
    def human_input_fn(history: TextInputOutputHistory) -> str:
        if False:
            ### DEBUG ONLY
            ### This will duplicate the menu print ... 
            for hist_str in history.tail(menus_only=True):
                builtins.print(f"[[HISTORY_PARSED_MENU_INFO]] {hist_str}")
        return builtins.input()
    humanio = AgentHistoryTextInputOutput(human_input_fn)
    def smart_auntie_fn(history: TextInputOutputHistory) -> str:
        can_roll_dice = False
        can_auto_purchase = False
        for hist_str in history.tail(menus_only=True):
            if "[[ALP]]" in hist_str:
                can_auto_purchase = True
                break # for(hist_str)
            if "[[RTD]]" in hist_str:
                can_roll_dice = True
                break # for(hist_str)
        if can_roll_dice:
            return "RTD"
        if can_auto_purchase:
            return "ALP"
        else:
            builtins.print("[[HUMAN_INPUT_REQUIRED]]")
            return builtins.input()
    smart_auntie_io = AgentHistoryTextInputOutput(smart_auntie_fn)
    if False:
        game.add_player({
            "name": "human",
            "textio": humanio,
        })
    if True:
        # auto_enter = True
        names = [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
        ]
        for name in names:
            game.add_player({
                "name": name,
                # "textio": DefaultTextInputOutput(print_prefix=name, auto_enter=auto_enter),
                "textio": smart_auntie_io,
            })
    game.run_main()
