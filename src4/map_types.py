from typing import ForwardRef


from src0.collections.bimap import Bimap
from src0.misc.settable_index import SettableIndex


Crossroad = ForwardRef("Crossroad")
Street = ForwardRef("Street")


class Crossroad:
    index: SettableIndex
    streets: Bimap[int, Street]

    def __init__(self, index: int = None) -> None:
        has_index = index is not None
        self.index = SettableIndex()
        if has_index:
            self.index.set(index)
        self.streets = Bimap[int, Street]()

    def add_street(self, street: Street) -> None:
        assert isinstance(street, Street)
        assert street.index.has_value()
        self.streets.add(street.index.value, street)

    def __repr__(self) -> str:
        text: list[str] = list()
        text.append("Crossroad(index=")
        text.append(repr(self.index))
        text.append(", streets=[")
        for iter_index, (street_index, street) in enumerate(self.streets):
            if iter_index >= 1:
                text.append(", ")
            text.append("S_" + str(street_index))
        text.append("]")
        text.append(")")
        return "".join(text)


class Street:
    index: SettableIndex
    crossroads: tuple[Crossroad, Crossroad]

    def __init__(self, index: int = None, cr_from: Crossroad = None, cr_to: Crossroad = None) -> None:
        has_index = index is not None
        has_from = cr_from is not None
        has_to = cr_to is not None
        if has_from:
            assert isinstance(cr_from, Crossroad)
        if has_to:
            assert isinstance(cr_to, Crossroad)
        if has_from and has_to:
            self.crossroads = (cr_from, cr_to)
        else:
            self.crossroads = None
        self.index = SettableIndex()
        if has_index:
            self.index.set(index)

    def has_crossroads(self) -> bool:
        return self.crossroads is not None and all(cr is not None for cr in self.crossroads)

    def __repr__(self) -> str:
        text: list[str] = list()
        if self.index.has_value():
            text.append("S_")
            text.append(repr(self.index))
            text.append("(crossroads=[")
        else:
            text.append("Street(crossroads=[")
        for iter_index, cr in enumerate(self.crossroads):
            if iter_index >= 1:
                text.append(", ")
            if cr.index.has_value():
                text.append("CR_")
                text.append(repr(cr.index))
            else:
                text.append(repr(cr))
        text.append("]")
        text.append(")")
        return "".join(text)
