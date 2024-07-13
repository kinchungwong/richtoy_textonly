from collections.abc import Sequence, Iterable
from typing import Any, Callable, Protocol, NamedTuple, Optional


from src2.code_utils import *
from src2.game_enums import *


PlayerIndex = int
SpaceIndex = int


class Player(HasTaggedIndex):
    name: str
    def __init__(
        self,
        index: int,
        name: str,
    ) -> None:
        self.index = index
        self.name = name


class Space(HasTaggedIndex):
    space_type_name: SpaceTypeName
    color_group_name: ColorGroupName
    owner: Optional[Player]

    def __init__(
        self,
        index: int,
        space_type_name: SpaceTypeName,
        color_group_name: ColorGroupName
    ) -> None:
        self.index = index
        self.space_type_name = space_type_name
        self.color_group_name = color_group_name
        self.owner = None


class GameBoard(Sequence[Space]):
    spaces: list[Space]
    connections: list[list[SpaceIndex]]

    def __init__(
        self,
    ) -> None:
        self.spaces = list()
        self.connections = list()

    def __len__(self) -> int:
        return len(self.spaces)

    def __getitem__(self, idx: int) -> Space:
        return self.spaces[idx]

    def iter_by_type(
        self,
        space_type_name: SpaceTypeName,
    ) -> Iterable[Space]:
        assert isinstance(space_type_name, SpaceTypeName)
        for space in self.spaces:
            if space.space_type_name is space_type_name:
                yield space

    def iter_by_owner(
        self, 
        owner: Player,
    ) -> Iterable[Space]:
        assert isinstance(owner, Player)
        for space in self.spaces:
            if space.owner is None:
                continue
            if space.owner is owner:
                yield space

    def iter_by_color(
        self,
        color_group_name: ColorGroupName,
    ) -> Iterable[Space]:
        assert isinstance(color_group_name, ColorGroupName)
        for space in self.spaces:
            if space.color_group_name is color_group_name:
                yield space

    def iter_by_fn(
        self, 
        predicate_fn: Callable[[Space], bool],
    ) -> Iterable[Space]:
        for space in self.spaces:
            if predicate_fn(space):
                yield space

