import builtins
import random
from typing import NamedTuple, Any, Literal
from dataclasses import dataclass


from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.player_sys import PlayerInfo, PlayerStatus, Player, NOBODY
from src.board_sys import BoardInfo, BoardStatus, Board
from src.square_sys import SquareInfo, SquareStatus, Square
from src.game_sys import GameInfo, GameStatus, Game
from src.textio_sys import TextInputOutputBase, DefaultTextInputOutput, BroadcastTextInputOutput

class TextBasedGame:
    NUM_SQUARES: Literal[100] = 100
    game: Game
    players: list[Player]
    broadcast: BroadcastTextInputOutput

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
        name = player.info.name
        player.textio.print(f"Player {name} is in prison.")

    def run_player_normal_turn(self):
        self.game.status.cur_walk = self.roll_the_dice()
        while not self.is_walk_finished():
            self.walk_single_step()
        self.walk_finished()
        self.game.status.cur_walk = None

    def roll_the_dice(self) -> WalkSession:
        cur_round = self.game.status.cur_round
        player = self.game.status.cur_player
        name = player.info.name
        player.textio.print(f"Player {name}, please roll the dice. (Press the enter key.)")
        _ = player.textio.input()
        dices = [
            random.randint(1, 6),
            random.randint(1, 6),
        ]
        move_points = sum(dices)
        player.textio.print(f"{name}, you rolled {dices[0]}, {dices[1]}, so you will walk {move_points} squares.")
        walk_session = WalkSession(
            info=WalkInfo(
                game_round=cur_round,
                player_index=player.info.index,
                move_points=move_points,
            ),
            status=WalkStatus(),
        )
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
        ###
        ### New version, work in progress.
        ### Has not been completely proof-read.
        ###
        player = self.game.status.cur_player
        name = player.info.name
        location = player.status.location
        square = self.game.get_board().get_square(location)
        can_purchase = square.info.can_purchase
        owner_index = square.status.owner_index if can_purchase else NOBODY
        has_owner = owner_index != NOBODY
        owner = self.players[owner_index] if has_owner else None
        owner_is_player = has_owner and (owner_index == player.info.index)
        owner_name = owner.info.name if has_owner else "STR_POISON_VALUE"
        land_value = square.get_land_value() if can_purchase else None
        land_rent = square.get_rent() if can_purchase else None
        player_money = player.status.money
        can_purchase_now = can_purchase and not has_owner and (player_money >= land_value)
        need_pay_rent = has_owner and not owner_is_player and not owner.status.in_prison
        can_pay_rent_now = need_pay_rent and (player_money >= land_rent)
        will_go_to_prison = need_pay_rent and not can_pay_rent_now
        def land_purchase_tx():
            assert can_purchase_now
            nonlocal player_money
            player.status.money -= land_value
            square.status.owner_index = player.info.index
            player_money = player.status.money
        def pay_rent_tx():
            assert can_pay_rent_now
            nonlocal player_money
            player.status.money -= land_rent
            owner.status.money += land_rent
            player_money = player.status.money
        def go_to_prison_tx():
            assert will_go_to_prison
            player.status.in_prison = True
        def land_info_io():
            player.textio.print(f"This land can be purchased and isn't owned yet.")
            player.textio.print(f"Its current land value is {land_value}.")
            player.textio.print(f"You have {player_money} dollars.")
        def land_purchase_offer_io():
            assert can_purchase_now
            player.textio.print(f"You can buy this land. Do you want to?")
        def land_purchase_accepted_io():
            assert can_purchase_now
            # NOTE player_money has been updated to the new value
            player.textio.print(f"I hear you say yes.")
            player.textio.print(f"Square {location} is now yours.")
            player.textio.print(f"You now have {player_money} dollars.")
        def land_purchase_declined_tx():
            assert can_purchase_now
            # NOTE future design, not implemented yet.
            if hasattr(player.status, "patience"):
                player.status.patience += 1
        def land_purchase_declined_io():
            assert can_purchase_now
            player.textio.print(f"What a careful decision. May your wisdon grow each day.")
        def rent_info_io():
            assert need_pay_rent
            player.textio.print(f"This land is owned by {owner_name}.")
            player.textio.print(f"You must pay rent, which is {land_rent}.")
        def rent_pay_success_io():
            assert need_pay_rent
            assert can_pay_rent_now
            player.textio.print(f"You now have {player_money} dollars.")
            owner.textio.print(f"Player {player.info.name} has paid you {land_rent} dollars of rent.")
        def rent_pay_failure_io():
            assert need_pay_rent
            assert not can_pay_rent_now
            assert will_go_to_prison
            player.textio.print(f"Unfortunately, you don't have the money to pay rent, therefore you are now in prison.")
            owner.textio.print(f"Player {player.info.name} was unable to pay the rent of {land_rent} dollars, and was sent to prison.")
        def special_square_io():
            player.textio.print(f"You've arrived at a special square.")

    def walk_finished(self):
        ###
        ### Old version.
        ### See "on_walk_finished()" which is the new version.
        ###
        player = self.game.status.cur_player
        name = player.info.name
        location = player.status.location
        player.textio.print(f"Player {name}, you're now at square {location}.")
        square = self.game.get_board().get_square(location)
        can_purchase = square.info.can_purchase
        owner_index = square.status.owner_index
        if can_purchase:
            land_value = square.get_land_value()
            land_rent = square.get_rent()
            player_money = player.status.money
            can_afford = player_money >= land_value
            if owner_index == NOBODY:
                player.textio.print(f"This land can be purchased and isn't owned yet.")
                player.textio.print(f"Its current land value is {land_value}.")
                player.textio.print(f"You have {player_money} dollars.")
                if can_afford:
                    player.textio.print(f"You can buy this land. Do you want to?")
                    player.textio.print(f"I hear you say yes.")
                    player.status.money -= land_value
                    square.status.owner_index = player.info.index
                    player.textio.print(f"Square {location} is now yours.")
                    ### Reload new value
                    player_money = player.status.money
                    player.textio.print(f"You now have {player_money} dollars.")
                else:
                    player.textio.print(f"You do not have the money to buy this land.")
            elif owner_index == player.info.index:
                player.textio.print(f"You own this land.")
            else:
                owner = self.players[owner_index]
                owner_name = owner.info.name
                player.textio.print(f"This land is owned by {owner_name}.")
                player.textio.print(f"You must pay rent, which is {land_rent}.")
                if player.status.money >= land_rent:
                    player.status.money -= land_rent
                    owner.status.money += land_rent
                    ### Reload new value
                    player_money = player.status.money
                    player.textio.print(f"You now have {player_money} dollars.")
                    owner.textio.print(f"Player {player.info.name} has paid you {land_rent} dollars of rent.")
                else:
                    player.textio.print(f"Unfortunately, you don't have the money to pay rent, therefore you are now in prison.")
                    owner.textio.print(f"Player {player.info.name} was unable to pay the rent of {land_rent} dollars, and was sent to prison.")
                    player.status.in_prison = True
        else:
            player.textio.print(f"You've arrived at a special square.")

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
    auto_enter = True
    names = [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
    ]
    for name in names:
        game.add_player({
            "name": name,
            "textio": DefaultTextInputOutput(print_prefix=name, auto_enter=auto_enter),
        })
    game.run_main()
