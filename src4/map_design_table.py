from collections.abc import Sequence
import builtins
import typing
from typing import TypeVar, Generic, Iterable, Callable, Optional, Union, ForwardRef


from src0.collections.unique_list import UniqueList
from src0.collections.bimap import Bimap


from src4.settable_index import SettableIndex
from src4.map_types import Crossroad, Street


class MapDesignTable:
    crossroads: UniqueList[Crossroad]
    streets: UniqueList[Street]

    def __init__(self) -> None:
        self.crossroads = UniqueList[Crossroad](typecheck=Crossroad)
        self.streets = UniqueList[Street](typecheck=Street)

    def add_crossroad(self, crossroad: Crossroad = None) -> Crossroad:
        if crossroad is None:
            crossroad = Crossroad()
        else:
            assert isinstance(crossroad, Crossroad)
        index = self.crossroads.add(crossroad)
        crossroad.index.value = index
        return crossroad

    def add_street(self, street: Street = None) -> Street:
        if street is None:
            street = Street()
        else:
            assert isinstance(street, Street)
        index = self.streets.add(street)
        street.index.value = index
        if street.has_crossroads():
            street.crossroads[0].add_street(street)
            street.crossroads[1].add_street(street)
        return street
