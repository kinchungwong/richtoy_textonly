# About this code
#
# The function, TextBasedGame.walk_finished(), was the first implementation of 
# the code that describes what happens after the player has finished walking
# the squares according to the dice-rolling result.
#
# Being the first implementation, and myself being unfamiliar with the official
# rules of Monopoly, many features documented in the original game were not
# implemented.
#
# Moreover, there is no text input. The menu system hasn't been implemented
# yet. The function has to assume that the player always say "yes" when given
# the opportunity to buy a land, and will compulsively do so until the player
# has no money left.
#
# This code is removed from the code base, and preserved here, as a demo of
# what would happen if interactive text-based gameplay were to be scripted
# (coded imperatively).
#
# Later on, we will gradually introduce the reasons why such coding style
# will fall short of meeting the game's implementation requirement.
#
# One such requirement is the ability to call upon a bank's mortgage
# service, at any time, even when the player is confronted with an
# immediate demand for rent payment.
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
