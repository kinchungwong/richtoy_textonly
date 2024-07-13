import builtins
from collections.abc import Sequence, Iterable
import itertools
from typing import Any, Callable, Protocol, NamedTuple, Optional, Union


from src2.code_utils import *
from src2.game_enums import *
from src2.diag_util import SupportsTextDiagnostics


class HasPostInitIndex(HasIndex):
    """
    Behaviors:
        __init__() will set index attribute to INDEX_NOT_INITIALIZED
        (index == -1).

        set_index(index) must be called, exactly once, to set it
        to a valid zero-based index value.
    
    How to use:
        This base class is used by builders that allow items to be
        constructed first, prior to their item index being known.
    """

    def __init__(self) -> None:
        super().__init__()
        self.index = self.INDEX_NOT_INITIALIZED
    
    def set_index(self, index: int) -> None:
        assert index >= 0
        assert self.index == self.INDEX_NOT_INITIALIZED
        self.index = index


class CrossroadBuilder(HasPostInitIndex):
    """
    Attributes:
        st_lat: int
            The zero-based index for identifying the n-th "horizontal", or 
            east-west-going street, numbered from top to bottom.
        st_lon: int
            The zero-based index for identifying the n-th "vertical", or
            north-south-going street, numbered from left to right.
    """
    st_lat: int
    st_lon: int

    def __init__(self, st_lat: int, st_lon: int) -> None:
        super().__init__()
        self.st_lat = st_lat
        self.st_lon = st_lon

    def __str__(self) -> str:
        return f"Crossroad[{self.index}] (at lat={self.st_lat}, lon={self.st_lon})"


class StreetBuilder(HasPostInitIndex):
    """
    Attributes:
        crossroads: tuple[CrossroadBuilder, CrossroadBuilder] 
            Identifies the two crossroads that make the beginning and
            the end of the street.

        spaces_in_between: int
            Number of non-crossroad spaces to be inserted into
            the street, in between the two crossroad spaces.
    """
    crossroads: tuple[CrossroadBuilder, CrossroadBuilder]
    spaces_in_between: int

    def __init__(
        self,
        crossroads: tuple[CrossroadBuilder, CrossroadBuilder],
        spaces_in_between: int,
    ) -> None:
        super().__init__()
        self.crossroads = crossroads
        self.spaces_in_between = spaces_in_between

    def __str__(self) -> str:
        c1, c2 = self.crossroads
        return f"Street[{self.index}] (between crossroads {c1.index}, {c2.index})"


class SpaceBuilder(HasPostInitIndex):
    street_index: int
    street_space_index: int
    crossroad_index: int
    connections: list[int]
    
    def __init__(
        self,
        street_index: int = -1,
        street_space_index: int = -1,
        crossroad_index: int = -1,
    ) -> None:
        super().__init__()
        self.street_index = street_index
        self.street_space_index = street_space_index
        self.crossroad_index = crossroad_index
        self.connections = []
        assert self.is_from_street ^ self.is_from_crossroad

    @property
    def is_from_street(self) -> bool:
        return (self.street_index >= 0) and (self.street_space_index >= 0)
    
    @property
    def is_from_crossroad(self) -> bool:
        return (self.crossroad_index >= 0)

    def connect(self, other_space_index: int) -> None:
        assert self.index >= 0
        assert other_space_index >= 0
        if other_space_index == self.index:
            return
        if other_space_index in self.connections:
            return
        self.connections.append(other_space_index)

    def __str__(self) -> str:
        if self.street_index >= 0:
            return f"Space[{self.index}] (from street {self.street_index}, subspace {self.street_space_index})"
        else:
            return f"Space[{self.index}] (from crossroad {self.crossroad_index})"


class GridMapBuilder(SupportsTextDiagnostics):
    """
    Init attributes:
        num_lats: int
            Number of "horizontal", or east-west-going streets.
            These are arranged from top to bottom.

        num_lons: int
            Number of "vertical", or north-south-going streets.
            These are arranged from left to right.

        spaces_in_between: int
            Number of usable spaces on each street, excluding
            the crossroad spaces where streets meet together.

    Post-init attributes:
        crossroads: list[list[CrossroadBuilder]]
            Crossroads are the spaces at the intersection
            of streets, which can be looked up as 
            crossroads[lat][lon]

        lat_streets: list[list[StreetBuilder]]
            Streets that are horizontal, or east-west-going.

        lon_streets: list[list[StreetBuilder]]
            Streets that are vertical, or north-south-going.

        streets: list[StreetBuilder]
            Flattened list of streets containing all of
            lat_streets and lon_streets.
        
        spaces_by_street: list[list[SpaceBuilder]]
            Non-crossroad spaces, organized by the streets where
            they are located.

        spaces: list[SpaceBuilder]
            All spaces, including everything in spaces_by_street
            as well as crossroad spaces, the latter of which will
            be assigned item index strictly higher then the former.
    """

    num_lats: int
    num_lons: int
    spaces_in_between: int
    crossroads_by_latlon: list[list[CrossroadBuilder]]
    crossroads: list[CrossroadBuilder]
    lat_streets: list[list[StreetBuilder]]
    lon_streets: list[list[StreetBuilder]]
    streets: list[StreetBuilder]
    spaces_by_street: list[list[SpaceBuilder]]
    spaces_from_crossroads: list[SpaceBuilder]
    spaces: list[SpaceBuilder]

    def __init__(
        self,
        num_lats: int,
        num_lons: int,
        spaces_in_between: int,
    ) -> None:
        super().__init__()
        self.num_lats = num_lats
        self.num_lons = num_lons
        self.spaces_in_between = spaces_in_between
        self.init_crossroads_by_latlon()
        self.init_crossroads_flattened()
        self.init_lat_streets()
        self.init_lon_streets()
        self.init_streets_flattened()
        self.init_spaces_by_street()
        self.init_spaces_from_crossroads()
        self.init_spaces_flattened()
        self.connect_spaces()

    def init_crossroads_by_latlon(self) -> None:
        self.crossroads_by_latlon = [
            [
                CrossroadBuilder(
                    st_lat=st_lat,
                    st_lon=st_lon,
                )
                for st_lon in range(self.num_lons)
            ]
            for st_lat in range(self.num_lats)
        ]

    def init_crossroads_flattened(self) -> None:
        self.crossroads = list(
            itertools.chain.from_iterable(self.crossroads_by_latlon),
        )
        for crossroad_index, crossroad in enumerate(self.crossroads):
            crossroad.set_index(crossroad_index)

    def init_lat_streets(self) -> None:
        """Initializes latitudinal (horizontal, or east-west-going) streets.
        """
        self.lat_streets = [
            [
                StreetBuilder(
                    crossroads=(
                        self.crossroads_by_latlon[lat][lon_first],
                        self.crossroads_by_latlon[lat][lon_first+1],
                    ),
                    spaces_in_between=self.spaces_in_between,
                )
                for lon_first in range(self.num_lons - 1)
            ]
            for lat in range(self.num_lats)
        ]

    def init_lon_streets(self) -> None:
        """Initializes longitudinal (vertical, or north-south-going) streets.
        """
        self.lon_streets = [
            [
                StreetBuilder(
                    crossroads=(
                        self.crossroads_by_latlon[lat_first][lon],
                        self.crossroads_by_latlon[lat_first+1][lon],
                    ),
                    spaces_in_between=self.spaces_in_between,
                )
                for lon in range(self.num_lons)
            ]
            for lat_first in range(self.num_lats - 1)
        ]

    def init_streets_flattened(self) -> None:
        def fn_iter_all_streets() -> Iterable[StreetBuilder]:
            for nested_streets_2 in (self.lat_streets, self.lon_streets):
                for nested_streets in nested_streets_2:
                    yield from nested_streets
        self.streets = list(fn_iter_all_streets())
        for street_index, street in enumerate(self.streets):
            street.set_index(street_index)

    def init_spaces_by_street(self) -> None:
        self.spaces_by_street = [
            [
                SpaceBuilder(
                    street_index=street.index,
                    street_space_index=street_space_index,
                )
                for street_space_index in range(street.spaces_in_between)
            ]
            for street in self.streets
        ]

    def init_spaces_from_crossroads(self) -> None:
        self.spaces_from_crossroads = [
            SpaceBuilder(
                crossroad_index=crossroad.index,
            )
            for crossroad in self.crossroads
        ]

    def init_spaces_flattened(self) -> None:
        self.spaces = list(itertools.chain(
            itertools.chain.from_iterable(self.spaces_by_street),
            self.spaces_from_crossroads,
        ))
        for space_index, space in enumerate(self.spaces):
            space.set_index(space_index)

    def connect_spaces(self) -> None:
        for street_spaces in self.spaces_by_street:
            for space in street_spaces:
                assert space.is_from_street
                street_index = space.street_index
                street_space_index = space.street_space_index
                street = self.streets[street_index]
                if street_space_index == 0:
                    space.connect(self.spaces_from_crossroads[street.crossroads[0].index].index)
                else:
                    space.connect(street_spaces[street_space_index - 1].index)
                if street_space_index + 1 < street.spaces_in_between:
                    space.connect(street_spaces[street_space_index + 1].index)
                else:
                    space.connect(self.spaces_from_crossroads[street.crossroads[1].index].index)
        for space in self.spaces_from_crossroads:
            assert space.is_from_crossroad
            crossroad_index = space.crossroad_index
            ### TODO incomplete


if __name__ == "__main__":
    builder = GridMapBuilder(
        num_lats = 5,
        num_lons = 5,
        spaces_in_between = 3,
    )
    print(builder.textdiag.str())
    builder.textdiag.print()
