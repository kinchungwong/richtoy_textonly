# About this code
#
# This is a preserved copy of an incomplete refactoring of the
# function TextBasedGame.walk_finished().
#
# Being incomplete, the function has no effect when executed.
#
# The refactoring consisted of these steps:
#
#   1. Moving as much pure logic and computations (also known as 
#      "side-effect-free" code, or pure combinational logic)
#      to the beginning of the function.
#
#   2. While doing so, it is apparent that some variables can
#      only be populated under certain conditions.
#      We leverage Python's None as much as possible.
#
#   3. Later, we will structure the code to make sure that
#      code can only be executed when the conditions are met,
#      and that variables needed for code execution are always
#      populated, guaranteed by the conditions.
#
#   4. Finally, we classify all code into the following:
#      4.1 Pure computations
#      4.2 Pure input/output (text based)
#      4.3 Transactions (a bunch of state changes that must
#          either complete or be rolled back completely)
#
# This preserved copy was approximately somewhere between step 2 and 3
# when the decision was made to switch to a new coding approach.
#
# A skeleton of the data classes needed by the function were included,
# for the sake of syntax coloring.

class TextInputOutputBase:
    def print(self, *args, **kwargs):
        pass
    def input(self) -> str:
        pass

PlayerIndex = int
Location = int
NOBODY: PlayerIndex = -1

class SquareInfo:
    can_purchase: bool

class SquareStatus:
    owner_index: PlayerIndex

class Square:
    location: Location
    info: SquareInfo
    status: SquareStatus
    def get_land_value(self) -> int:
        pass
    def get_rent(self) -> int:
        pass

class PlayerInfo:
    index: PlayerIndex
    name: str

class PlayerStatus:
    location: Location
    money: int
    in_prison: bool

class Player:
    info: PlayerInfo
    status: PlayerStatus
    textio: TextInputOutputBase

class Board:
    def get_square(self, location: Location) -> Square:
        pass

class GameInfo:
    pass

class GameStatus:
    cur_player: Player

class Game:
    info: GameInfo
    status: GameStatus
    def get_board(self) -> Board:
        pass

class TextBasedGame:
    game: Game
    players: list[Player]

    def on_walk_finished(self):
        ###
        ### New version, work in progress.
        ### Has not been completely proof-read.
        ###
        player = self.game.status.cur_player
        player_io = player.textio
        location = player.status.location
        square = self.game.get_board().get_square(location)
        can_purchase = square.info.can_purchase
        is_special_square = not can_purchase
        owner_index = square.status.owner_index if can_purchase else NOBODY
        has_owner = owner_index != NOBODY
        owner = self.players[owner_index] if has_owner else None
        owner_is_player = has_owner and (owner_index == player.info.index)
        owner_name = owner.info.name if has_owner else "STR_POISON_VALUE"
        owner_io = owner.textio if has_owner else None
        land_value = square.get_land_value() if can_purchase else None
        land_rent = square.get_rent() if can_purchase else None
        player_money = player.status.money
        can_purchase_now = can_purchase and not has_owner and (player_money >= land_value)
        need_pay_rent = has_owner and not owner_is_player and not owner.status.in_prison
        can_pay_rent_now = need_pay_rent and (player_money >= land_rent)
        will_go_to_prison = need_pay_rent and not can_pay_rent_now
        def pay_rent_tx():
            assert can_pay_rent_now
            nonlocal player_money
            player.status.money -= land_rent
            owner.status.money += land_rent
            player_money = player.status.money
        def go_to_prison_tx():
            assert will_go_to_prison
            player.status.in_prison = True
        def rent_pay_success_io():
            assert has_owner
            assert not owner_is_player
            assert need_pay_rent
            assert can_pay_rent_now
            player_io.print(f"You now have {player_money} dollars.")
            owner_io.print(f"Player {player.info.name} has paid you {land_rent} dollars of rent.")
        def rent_pay_failure_io():
            assert has_owner
            assert not owner_is_player
            assert need_pay_rent
            assert not can_pay_rent_now
            assert will_go_to_prison
            player_io.print(f"Unfortunately, you don't have the money to pay rent, therefore you are now in prison.")
            owner_io.print(f"Player {player.info.name} was unable to pay the rent of {land_rent} dollars, and was sent to prison.")
        def special_square_io():
            assert is_special_square
            player_io.print(f"You've arrived at a special square.")
