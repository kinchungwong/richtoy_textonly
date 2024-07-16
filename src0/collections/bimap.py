from collections.abc import Collection, Mapping, Sequence
import typing
from typing import TypeVar, Generic, Iterable


_Left_Bimap = TypeVar("_Left_Bimap")
_Right_Bimap = TypeVar("_Right_Bimap")
Bimap = TypeVar("Bimap")


class Bimap(Generic[_Left_Bimap, _Right_Bimap], Collection[tuple[_Left_Bimap, _Right_Bimap]]):
    _ltr: dict[_Left_Bimap, _Right_Bimap]
    _rtl: dict[_Right_Bimap, _Left_Bimap]

    def __init__(self) -> None:
        self._ltr = dict()
        self._rtl = dict()

    def add(self, left: _Left_Bimap, right: _Right_Bimap) -> None:
        left_exist = left in self._ltr
        right_exist = right in self._rtl
        should_raise = False
        if not left_exist and not right_exist:
            self._ltr[left] = right
            self._rtl[right] = left
        elif left_exist and right_exist:
            should_raise = self._ltr[left] != right or self._rtl[right] != left
        else:
            should_raise = True
        if should_raise:
            raise self.BimapTupleConflictError(
                orig_left=self._rtl.get(right, None), 
                orig_right=self._ltr.get(left, None),
                new_left=left,
                new_right=right,
            )

    def to_right(self, left: _Left_Bimap, default: typing.Any = None):
        return self._ltr(left, default)

    def to_left(self, right: _Right_Bimap, default: typing.Any = None):
        return self._rtl(right, default)
    
    def with_left(self, left: _Left_Bimap, default: typing.Any = None):
        if left in self._ltr:
            return (left, self._ltr[left])
        else:
            return default

    def with_right(self, right: _Right_Bimap, default: typing.Any = None):
        if right in self._rtl:
            return (self._rtl[right], right)
        else:
            return default

    def __iter__(self) -> Iterable[tuple[_Left_Bimap, _Right_Bimap]]:
        yield from self._ltr.items()

    def __len__(self) -> int:
        return len(self._ltr)
    
    def __contains__(self, tup: typing.Any) -> bool:
        if tup is None:
            return False
        if type(tup) == tuple and len(tup) == 2:
            return tup[0] in self._ltr and tup[1] in self._rtl and self._ltr[tup[0]] == tup[1]
        else:
            return tup in self._ltr
    
    def copy(self):
        other = Bimap[_Left_Bimap, _Right_Bimap]()
        other._ltr = self._ltr.copy()
        other._rtl = self._rtl.copy()
        return other

    def copy_flipped(self):
        other = Bimap[_Right_Bimap, _Left_Bimap]()
        other._ltr = self._rtl.copy()
        other._rtl = self._ltr.copy()
        return other

    def __repr__(self) -> str:
        text: list[str] = list()
        text.append("Bimap([")
        for iter_idx, (left, right) in enumerate(self._ltr.items()):
            if iter_idx >= 1:
                text.append(", ")
            text.append("(")
            text.append(repr(left))
            text.append(", ")
            text.append(repr(right))
            text.append(")")
        text.append("])")
        return "".join(text)


    class BimapException(Exception):
        _args: Sequence[typing.Any]
        _kwargs: Mapping[str, typing.Any]
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(args, kwargs)
            self._args = args
            self._kwargs = kwargs

    class BimapTupleConflictError(BimapException):
        pass
