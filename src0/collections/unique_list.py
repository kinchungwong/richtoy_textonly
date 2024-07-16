import builtins
from collections.abc import Sequence, Mapping
import inspect
import typing
from typing import TypeVar, Generic, Iterable, Callable, Optional, Union, Protocol


_T_UniqueList = TypeVar("_T_UniqueList")
_Self_UniqueList = TypeVar("_Self_UniqueList", bound="UniqueList")


class UniqueList(Generic[_T_UniqueList], Sequence[_T_UniqueList]):
    _items: list[_T_UniqueList]
    _lookup: dict[_T_UniqueList, int]
    _typecheck: Callable[[typing.Any], bool]
    _expected_type: Optional[type]

    def __init__(
        self, 
        items: Iterable[_T_UniqueList] = None,
        typecheck: Union[bool, type, Callable[[typing.Any], bool]] = False,
    ) -> None:
        self._items = list()
        self._lookup = dict()
        self._init_typecheck(typecheck)
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item: _T_UniqueList) -> int:
        self._item_type_else_raise(item)
        item_idx = self._lookup.get(item, -1)
        if item_idx >= 0:
            return item_idx
        item_idx = len(self._items)
        self._items.append(item)
        self._lookup[item] = item_idx
        return item_idx

    def get(self, idx: int, default: typing.Any = None):
        if 0 <= idx < len(self._items):
            return self._items[idx]
        else:
            return default
    
    def index(self, item: _T_UniqueList, default: int = -1) -> int:
        self._item_type_else_raise(item)
        return self._lookup.get(item, default)

    def __getitem__(self, idx: int) -> _T_UniqueList:
        result = self.get(idx)
        if result is None:
            raise self.BadIndexException(f"UniqueList: idx violates (0 <= (idx: {idx}) < (len: {len(self._items)}))")
        return result
    
    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterable[_T_UniqueList]:
        yield from self._items

    def enumerate(self) -> Iterable[tuple[int, _T_UniqueList]]:
        for idx, item in enumerate(self._items):
            yield (idx, item)

    def items(self) -> Iterable[tuple[_T_UniqueList, int]]:
        for idx, item in enumerate(self._items):
            yield (item, idx)

    def clear(self) -> None:
        self._items.clear()
        self._lookup.clear()

    def sorted(self: _Self_UniqueList, reverse: bool = False) -> _Self_UniqueList:
        items_list = list(self.items())
        items_list.sort(reverse=reverse)
        return UniqueList[_T_UniqueList](item for item, _ in items_list)

    def __repr__(self) -> str:
        classname = type(self).__name__
        text: list[str] = list()
        text.append(classname)
        text.append("([")
        for idx, item in enumerate(self._items):
            if idx > 0:
                text.append(", ")
            text.append(repr(item))
        text.append("])")
        return "".join(text)

    def _item_type_else_raise(self, item: typing.Any) -> None:
        if self._typecheck is None:
            return
        if not self._typecheck(item):
            inspect_typecheck = inspect.getsource(self._typecheck)
            raise self.ItemTypeException(
                item=item, 
                item_type=type(item),
                expected_type=self._expected_type,
                typecheck=inspect_typecheck, 
            )

    def _init_typecheck(
        self, 
        typecheck: Union[bool, type, Callable[[typing.Any], bool]],
    ) -> None:
        self._typecheck = None
        self._expected_type = None
        if typecheck is None or typecheck is False:
            return
        if typecheck is True:
            # expected_type = typing.get_args(...)
            raise self.TypeCheckSupportNotImplemented()
        elif type(typecheck) == type or issubclass(typecheck, (type, Protocol)):
            self._expected_type = typecheck
        elif builtins.callable(typecheck):
            self._typecheck = typecheck
        else:
            raise Exception(f"Unable to process typecheck argument: {type(typecheck)}, {str(typecheck)}")
        if self._typecheck is None and self._expected_type is not None:
            def fn_typecheck_auto(item: typing.Any) -> bool:
                return item is not None and isinstance(item, self._expected_type)
            self._typecheck = fn_typecheck_auto


    class UniqueListException(Exception):
        _args: Sequence[typing.Any]
        _kwargs: Mapping[str, typing.Any]
        def __init__(self, *args, **kwargs) -> None:
            self._args = args
            self._kwargs = kwargs
            super().__init__(self._args, self._kwargs)

    class BadIndexException(UniqueListException):
        pass

    class ItemNotFoundException(UniqueListException):
        pass

    class ItemTypeException(UniqueListException):
        EXC_MESSAGE = "UniqueList: bad item type."
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*[self.EXC_MESSAGE, *args], **kwargs)

    class TypeCheckSupportNotImplemented(UniqueListException):
        EXC_MESSAGE = "As of Python 3.11 has no access to the type-erased type argument inside a generic class."
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*[self.EXC_MESSAGE, *args], **kwargs)
