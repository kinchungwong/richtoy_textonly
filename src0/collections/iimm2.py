###
### Yet another draft version of IntIntMultimap
###

import collections
from collections.abc import MutableSet, Mapping, Iterable, Collection
import typing
from typing import TypeVar, ForwardRef, Union, Protocol
from typing import overload, runtime_checkable

_KT = int
_VT = int

IIMM2 = ForwardRef("IIMM2")
ItemsView = ForwardRef("ItemsView")
ValuesView = ForwardRef("ValuesView")


@runtime_checkable
class HasItemsView(Protocol):
    def add_item(self, key: _KT, value: _VT) -> bool: ...
    def discard_item(self, key: _KT, value: _VT) -> bool: ...
    def add_items(self, items: Iterable[tuple[_KT, _VT]]) -> int: ...
    def discard_items(self, items: Iterable[tuple[_KT, _VT]]) -> int: ...
    def items(self) -> ItemsView: ...
    def total(self) -> int: ...


@runtime_checkable
class HasValuesView(Protocol):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterable[_KT]: ...
    def __getitem__(self, key: _KT) -> ValuesView: ...


class IIMM2(Mapping[_KT, MutableSet[_VT]], HasItemsView, HasValuesView):
    _dict: dict[_KT, set[_VT]]
    _total: int
    _items: ItemsView

    def __init__(
        self,
        items: Iterable[tuple[_KT, _VT]] = None,
        other: HasItemsView = None,
    ) -> None:
        if type(self) != IIMM2:
            raise Exception("Subclassing not allowed.")
        self.clear()
        if items is not None:
            for k, v in items:
                self.add_item(k, v)
        if other is not None:
            for k, v in other.items():
                self.add_item(k, v)

    def clear(self) -> None:
        self._dict = dict()
        self._total = 0
        self._items = ItemsView(self)

    ### Begin of Mapping View

    def __len__(self) -> int:
        return len(self._dict)
    
    def __iter__(self) -> Iterable[_KT]:
        yield from self._dict

    def __getitem__(self, key: _KT) -> ValuesView:
        return ValuesView(self, key)

    ### Begin of Items View

    def items(self) -> ItemsView:
        return self._items
    
    def total(self) -> int:
        return self._total

    def add_item(self, *args, **kwargs) -> bool:
        _METHOD_NAME = f"{type(self).__name__}.add_item()"
        (k, v) = self._internal_parse_kv(_METHOD_NAME, *args, **kwargs)
        old_total = self._total
        if k not in self._dict:
            self._dict[k] = set[_VT](v)
            self._total += 1
        else:
            vs = self._dict[k]
            if v not in vs:
                vs.add(v)
                self._total += 1
        return self._total > old_total    

    def discard_item(self, *args, **kwargs) -> bool:
        _METHOD_NAME = f"{type(self).__name__}.discard_item()"
        (k, v) = self._internal_parse_kv(_METHOD_NAME, *args, **kwargs)
        if k not in self._dict:
            return False
        else:
            vs = self._dict[k]
            if v not in vs:
                return False
            vs.discard(v)
            self._total -= 1
            if len(vs) == 0:
                self._dict.pop(k)
            return True

    def add_items(self, items: Iterable[tuple[_KT, _VT]]) -> int:
        old_total = self._total
        for k, v in items:
            self.add_item(k, v)
        return self._total - old_total

    def discard_items(self, items: Iterable[tuple[_KT, _VT]]) -> int:
        old_total = self._total
        for k, v in items:
            self.discard_item(k, v)
        return old_total - self._total

    ### Overloads

    @overload
    def add_item(self, key: _KT, value: _VT) -> bool: ...

    @overload
    def add_item(self, key_value: tuple[_KT, _VT]) -> bool: ...

    @overload
    def discard_item(self, key: _KT, value: _VT) -> bool: ...

    @overload
    def discard_item(self, key_value: tuple[_KT, _VT]) -> bool: ...

    ### Internal methods

    def _internal_parse_kv(self, method_name: str, *args, **kwargs) -> tuple[_KT, _VT]:
        if len(args) > 0 and len(kwargs) > 0:
            raise Exception(f"{method_name}: cannot be called with a mix of positional and keyword arguments.")
        if len(kwargs) > 0:
            k = kwargs.get("key", default=None)
            v = kwargs.get("value", default=None)
            kv = kwargs.get("key_value", default=None)
            if (k is None) != (v is None):
                raise Exception(f"{method_name}: missing value for key or value.")
            if (int(k is not None) + int(kv is not None)) != 1:
                raise Exception(f"{method_name}: redundant arguments for key and value.")
            if kv is not None:
                k = kv[0]
                v = kv[1]
            if type(k) != _KT:
                raise Exception(f"{method_name}: Wrong key type.")
            if type(v) != _VT:
                raise Exception(f"{method_name}: Wrong value type.")
        else:
            if len(args) == 1 and type(args[0]) == tuple and type(args[0][0]) == _KT and type(args[0][1]) == _VT:
                k = args[0][0]
                v = args[0][1]
            elif len(args) == 2 and type(args[0]) == _KT and type(args[1]) == _VT:
                k = args[0]
                v = args[1]
            else:
                raise Exception(f"{method_name}: Incorrect arguments.")
        return (k, v)


class ItemsView(MutableSet[tuple[_KT, _VT]]):
    _iimm: IIMM2

    def __init__(self, iimm: IIMM2) -> None:
        if type(self) != ItemsView:
            raise Exception("Subclassing not allowed.")
        if type(iimm) != IIMM2:
            raise Exception("Subclassing not allowed.")
        self._iimm = iimm

    def __len__(self) -> int:
        return self._iimm._total

    @overload
    def __contains__(self, key: _KT) -> bool: ...

    @overload
    def __contains__(self, key_value_pair: tuple[_KT, _VT]) -> bool: ...

    def __contains__(self, k_or_kv: Union[_KT, tuple[_KT, _VT]]) -> bool:
        if type(k_or_kv) == _KT:
            k = k_or_kv
            return self._iimm._dict.__contains__(k)
        elif type(k_or_kv) == tuple and len(k_or_kv) == 2 and type(k_or_kv[0]) == _KT and type(k_or_kv[1]) == _VT:
            k = k_or_kv[0]
            v = k_or_kv[1]
            return self._iimm._dict.__contains__(k) and self._iimm._dict.__getitem__(k).__contains__(v)
        else:
            raise Exception()

    def __iter__(self) -> Iterable[tuple[_KT, _VT]]:
        for k, vs in self._iimm._dict.items():
            for v in vs:
                yield (k, v)

    @overload
    def add(self, key: _KT, value: _VT) -> None: ...

    @overload
    def add(self, key_value: tuple[_KT, _VT]) -> None: ...

    @overload
    def discard(self, key: _KT, value: _VT) -> None: ...

    @overload
    def discard(self, key_value: tuple[_KT, _VT]) -> None: ...

    def add(self, *args, **kwargs) -> None:
        self._iimm.add_item(*args, **kwargs)

    def discard(self, *args, **kwargs) -> None:
        self._iimm.discard_item(*args, **kwargs)
    
    def clear(self) -> None:
        self._iimm.clear()

    __le__ = None
    __lt__ = None
    __gt__ = None
    __ge__ = None
    __and__ = None
    __or__ = None
    __sub__ = None
    __xor__ = None
    __ior__ = None
    __iand__ = None
    __ixor__ = None
    __isub__ = None
    
    def __eq__(self, other: typing.Any) -> bool:
        return other is self
    
    def __ne__(self, other: typing.Any) -> bool:
        return other is not self

class ValuesView(collections.abc.ValuesView, Collection[_VT]):
    _iimm: IIMM2
    _set: set[_VT]

    def __init__(self, iimm: IIMM2, key: _KT) -> None:
        if type(self) != ValuesView:
            raise Exception("Subclassing not allowed.")
        if type(iimm) != IIMM2:
            raise Exception("Subclassing not allowed.")
        if type(key) != _KT:
            raise Exception("Wrong key type.")
        self._iimm = iimm
        if key in iimm._dict:
            self._set = iimm._dict[key]
        else:
            self._set = frozenset[_VT]()

    def __contains__(self, value: _VT) -> bool:
        return value in self._set
    
    def __iter__(self) -> Iterable[_VT]:
        yield from self._set

    def __len__(self) -> int:
        return len(self._set)
