import builtins
import random
from typing import NamedTuple, Any, Literal
from dataclasses import dataclass


from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.player_sys import PlayerInfo, PlayerStatus, Player, NOBODY
from src.board_sys import BoardInfo, BoardStatus, Board
from src.square_sys import SquareInfo, SquareStatus, Square
from src.game_sys import GameInfo, GameStatus, Game

class TextBasedGame:
    NUM_SQUARES: Literal[100] = 100
    game: Game
    players: list[Player]

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

    def _create_player_instance(self, detail: dict[str, Any]) -> Player:
        assert type(detail) == dict
        info_kw_list = set(["name", "index"])
        status_kw_list = set([])
        info_detail = { k:v for k, v in detail.items() if k in info_kw_list }
        status_detail = { k:v for k, v in detail.items() if k in status_kw_list }
        return Player(
            info=PlayerInfo(**info_detail),
            status=PlayerStatus(**status_detail),
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
        print(f"round {(cur_round)}, player {(player.info.index)}, name {player.info.name}")
        if player.status.in_prison:
            self.run_player_prison_turn()
        else:
            self.run_player_normal_turn()

    def run_player_prison_turn(self):
        name = self.game.status.cur_player.info.name
        print(f"Player {name} is in prison.")

    def run_player_normal_turn(self):
        self.game.status.cur_walk = self.roll_the_dice()
        while not self.is_walk_finished():
            self.walk_single_step()
        self.walk_finished()

    def roll_the_dice(self) -> WalkSession:
        cur_round = self.game.status.cur_round
        player = self.game.status.cur_player
        name = player.info.name
        _ = builtins.input(f"Player {name}, please roll the dice. (Press the enter key.)")
        dices = [
            random.randint(1, 6),
            random.randint(1, 6),
        ]
        move_points = sum(dices)
        print(f"{name}, you rolled {dices[0]}, {dices[1]}, so you will walk {move_points} squares.")
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

    def walk_finished(self):
        player = self.game.status.cur_player
        name = player.info.name
        location = player.status.location
        print(f"Player {name}, you're now at square {location}.")
        square = self.game.get_board().get_square(location)
        can_purchase = square.info.can_purchase
        owner_index = square.status.owner_index
        if can_purchase:
            land_value = square.get_land_value()
            land_rent = square.get_rent()
            player_money = player.status.money
            can_afford = player_money >= land_value
            if owner_index == NOBODY:
                print(f"This land can be purchased and isn't owned yet.")
                print(f"Its current land value is {land_value}.")
                print(f"You have {player_money} dollars.")
                if can_afford:
                    print(f"You can buy this land. Do you want to?")
                    print(f"I hear you say yes.")
                    player.status.money -= land_value
                    square.status.owner_index = player.info.index
                    print(f"Square {location} is now yours.")
                    ### Reload new value
                    player_money = player.status.money
                    print(f"You now have {player_money} dollars.")
                else:
                    print(f"You do not have the money to buy this land.")
            elif owner_index == player.info.index:
                print(f"You own this land.")
            else:
                owner = self.players[owner_index]
                print(f"This land is owned by {owner.info.name}.")
                print(f"You must pay rent, which is {land_rent}.")
                if player.status.money >= land_rent:
                    player.status.money -= land_rent
                    owner.status.money += land_rent
                    ### Reload new value
                    player_money = player.status.money
                    print(f"You now have {player_money} dollars.")
                else:
                    print(f"Unfortunately, you don't have the money to pay rent, therefore you are now in prison.")
                    player.status.in_prison = True
        else:
            print(f"You've arrived at a special square.")

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
            print("Game ended. All players have quit.")
        elif num_in_prison == total_players:
            print("Game ended. All players are in prison.")
        elif len(players_active) == 1:
            winner = players_active[0]
            winner_name = winner.info.name
            money = winner.status.money
            print(f"Game is won by {winner_name}, with {money} dollars at the end.")

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
    game.add_player({
        "name": "Alpha"
    })
    game.add_player({
        "name": "Beta"
    })
    game.add_player({
        "name": "Gamma"
    })
    game.add_player({
        "name": "Delta"
    })
    game.run_main()
