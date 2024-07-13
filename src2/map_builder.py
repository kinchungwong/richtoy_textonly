import builtins
from collections.abc import Iterable
import itertools
from typing import TypeVar


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


class Crossroad(HasPostInitIndex):
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


class Street(HasPostInitIndex):
    """
    Attributes:
        crossroads: tuple[Crossroad, Crossroad] 
            Identifies the two crossroads that make the beginning and
            the end of the street.

        subspaces_per_street: int
            Number of non-crossroad spaces to be inserted into
            the street, in between the two crossroad spaces.
    """
    crossroads: tuple[Crossroad, Crossroad]
    subspaces_per_street: int

    def __init__(
        self,
        crossroads: tuple[Crossroad, Crossroad],
        subspaces_per_street: int,
    ) -> None:
        super().__init__()
        self.crossroads = crossroads
        self.subspaces_per_street = subspaces_per_street

    def __str__(self) -> str:
        c1, c2 = self.crossroads
        return f"Street[{self.index}] (between crossroads {c1.index}, {c2.index})"


Space = TypeVar("Space")

class Space(HasPostInitIndex):
    street_index: int
    street_space_index: int
    crossroad_index: int
    connections: set[Space]
    
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
        self.connections = set()
        assert self.is_from_street ^ self.is_from_crossroad

    @property
    def is_from_street(self) -> bool:
        return (self.street_index >= 0) and (self.street_space_index >= 0)
    
    @property
    def is_from_crossroad(self) -> bool:
        return (self.crossroad_index >= 0)

    def connect(self, other: Space) -> None:
        """Connects two instances of Space, mutually.
        """
        assert type(other) == Space
        assert self.index >= 0
        assert other.index >= 0
        if other is self:
            return
        if other.index == self.index:
            return
        if other not in self.connections:
            self.connections.add(other)
        if self not in other.connections:
            other.connections.add(self)

    def __str__(self) -> str:
        num_conns = len(self.connections)
        if self.street_index >= 0:
            return f"Space[{self.index}] (from street {self.street_index}, subspace {self.street_space_index}, num_conns={num_conns})"
        else:
            return f"Space[{self.index}] (from crossroad {self.crossroad_index}, num_conns={num_conns})"

    def __hash__(self) -> int:
        assert self.index >= 0
        return builtins.hash(self.index)


class GridMapBuilder(SupportsTextDiagnostics):
    """
    Init attributes:
        num_lats: int
            Number of "horizontal", or east-west-going streets.
            These are arranged from top to bottom.

        num_lons: int
            Number of "vertical", or north-south-going streets.
            These are arranged from left to right.

        subspaces_per_street: int
            Number of usable spaces on each street, excluding
            the crossroad spaces where streets meet together.

    Post-init attributes:
        crossroads: list[list[Crossroad]]
            Crossroads are the spaces at the intersection
            of streets, which can be looked up as 
            crossroads[lat][lon]

        lat_streets: list[list[Street]]
            Streets that are horizontal, or east-west-going.

        lon_streets: list[list[Street]]
            Streets that are vertical, or north-south-going.

        streets: list[Street]
            Flattened list of streets containing all of
            lat_streets and lon_streets.
        
        spaces_by_street: list[list[Space]]
            Non-crossroad spaces, organized by the streets where
            they are located.

        spaces: list[Space]
            All spaces, including everything in spaces_by_street
            as well as crossroad spaces, the latter of which will
            be assigned item index strictly higher then the former.
    """

    num_lats: int
    num_lons: int
    subspaces_per_street: int
    crossroads_by_latlon: list[list[Crossroad]]
    crossroads: list[Crossroad]
    lat_streets: list[list[Street]]
    lon_streets: list[list[Street]]
    streets: list[Street]
    spaces_by_street: list[list[Space]]
    spaces_from_crossroads: list[Space]
    spaces: list[Space]

    def __init__(
        self,
        num_lats: int,
        num_lons: int,
        subspaces_per_street: int,
    ) -> None:
        super().__init__()
        self.num_lats = num_lats
        self.num_lons = num_lons
        self.subspaces_per_street = subspaces_per_street
        self.init_crossroads_by_latlon()
        self.init_crossroads_flattened()
        self.init_lat_streets()
        self.init_lon_streets()
        self.init_streets_flattened()
        self.init_spaces_by_street()
        self.init_spaces_from_crossroads()
        self.init_spaces_flattened()
        self.connect_street_subspaces()
        self.connect_street_crossroads()

    def init_crossroads_by_latlon(self) -> None:
        self.crossroads_by_latlon = [
            [
                Crossroad(
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
                Street(
                    crossroads=(
                        self.crossroads_by_latlon[lat][lon_first],
                        self.crossroads_by_latlon[lat][lon_first+1],
                    ),
                    subspaces_per_street=self.subspaces_per_street,
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
                Street(
                    crossroads=(
                        self.crossroads_by_latlon[lat_first][lon],
                        self.crossroads_by_latlon[lat_first+1][lon],
                    ),
                    subspaces_per_street=self.subspaces_per_street,
                )
                for lon in range(self.num_lons)
            ]
            for lat_first in range(self.num_lats - 1)
        ]

    def init_streets_flattened(self) -> None:
        def fn_iter_all_streets() -> Iterable[Street]:
            for nested_streets_2 in (self.lat_streets, self.lon_streets):
                for nested_streets in nested_streets_2:
                    yield from nested_streets
        self.streets = list(fn_iter_all_streets())
        for street_index, street in enumerate(self.streets):
            street.set_index(street_index)

    def init_spaces_by_street(self) -> None:
        self.spaces_by_street = list()
        for street in self.streets:
            num_subspaces = street.subspaces_per_street
            street_subspace: list[Space] = list()
            for subspace_index in range(num_subspaces):
                subspace = Space(
                    street_index=street.index,
                    street_space_index=subspace_index,
                )
                street_subspace.append(subspace)
            self.spaces_by_street.append(street_subspace)

    def init_spaces_from_crossroads(self) -> None:
        self.spaces_from_crossroads = [
            Space(
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

    def connect_street_subspaces(self) -> None:
        for street in self.streets:
            num_subspaces = street.subspaces_per_street
            street_subspace = self.spaces_by_street[street.index]
            for subspace_index in range(num_subspaces - 1):
                subspace_one = street_subspace[subspace_index]
                subspace_two = street_subspace[subspace_index + 1]
                ### mutually connected, by current design
                subspace_one.connect(subspace_two)

    def connect_street_crossroads(self) -> None:
        for street in self.streets:
            street_subspace = self.spaces_by_street[street.index]
            crossroad_begin, crossroad_end = street.crossroads
            space_crossroad_begin = self.spaces_from_crossroads[crossroad_begin.index]
            space_crossroad_end = self.spaces_from_crossroads[crossroad_end.index]
            subspace_first = street_subspace[0]
            subspace_first.connect(space_crossroad_begin)
            subspace_last = street_subspace[-1]
            subspace_last.connect(space_crossroad_end)


if __name__ == "__main__":
    builder = GridMapBuilder(
        num_lats = 5,
        num_lons = 5,
        subspaces_per_street = 3,
    )
    print(builder.textdiag.str())
    builder.textdiag.print()
