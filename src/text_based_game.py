import builtins
import random
from typing import NamedTuple, Any
from dataclasses import dataclass


from src.walk_sys import WalkInfo, WalkStatus, WalkSession
from src.player_sys import PlayerInfo, PlayerStatus, Player
from src.game_sys import GameInfo, GameStatus, Game


class TextBasedGame:
    game: Game
    players: list[Player]

    def __init__(self) -> None:
        self.game = Game(
            info=GameInfo(),
            status=GameStatus(),
        )
        self.players = []

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
        pass

    def run_player_normal_turn(self):
        self.game.status.cur_walk = self.roll_the_dice()
        while not self.is_walk_finished():
            self.walk_single_step()
        player = self.game.status.cur_player
        name = player.info.name
        print(f"Player {name}, you're now at square {player.status.location}.")

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
        psts.location = (psts.location + 1) % 100

    def is_game_playing(self) -> bool:
        num_playing = 0
        for player in self.players:
            if player.status.is_playing:
                num_playing += 1
                if num_playing >= 2:
                    return True
        return False

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
