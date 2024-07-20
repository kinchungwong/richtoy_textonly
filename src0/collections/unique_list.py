from collections.abc import Mapping, Sequence
import typing
from typing import Callable, Generic, Iterable, Protocol, TypeVar, Union


_T = TypeVar("_T")
_TypeCheckList = Union[type, tuple[type]]
_TypeCheckFunc = Callable[[typing.Any], bool]


class UniqueList(Generic[_T], Sequence[_T]):
    _items: list[_T]
    _lookup: dict[_T, int]
    _typecheck: Union[bool, _TypeCheckList, _TypeCheckFunc]
    _can_clear: bool

    def __init__(
        self,
        items: Iterable[_T] = None,
        typecheck: Union[bool, _TypeCheckList, _TypeCheckFunc] = False,
    ) -> None:
        """
        Initializes UniqueList, with options to pre-populate with items and
        specify how item types should be validated.

        Important:
            As of Python 3.11, the __init__() of a generic class instance
            does not have access to the type arguments. As a result,
            using typecheck=True will have no effect on items added as part
            of the __init__() function call.
        """
        self._items = list()
        self._lookup = dict()
        self._typecheck = typecheck
        self._can_clear = True ### unless disable_clear() is called
        if isinstance(items, Iterable):
            for item in items:
                self.add(item)

    def add(self, item: _T) -> int:
        self._validate_item(item)
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
    
    def index(self, item: _T, default: int = -1) -> int:
        self._validate_item(item)
        return self._lookup.get(item, default)

    def __getitem__(self, idx: int) -> _T:
        if 0 <= idx < len(self._items):
            return self._items[idx]
        else:
            raise self.BadIndexException(idx, len(self._items))
    
    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        yield from self._items

    def enumerate(self) -> Iterable[tuple[int, _T]]:
        for idx, item in enumerate(self._items):
            yield (idx, item)

    def items(self) -> Iterable[tuple[_T, int]]:
        for idx, item in enumerate(self._items):
            yield (item, idx)

    def clear(self) -> None:
        """Resets the UniqueList into an empty state. After resetting, 
        the number of items is zero, and any items added afterwards will
        start with index zero.
        """
        if not self._can_clear:
            raise self.InvalidClearOperationException()
        self._items.clear()
        self._lookup.clear()

    def disable_clear(self) -> None:
        """Disables the clear() functionality, making it strictly
        append-only. Once disabled, clear() cannot be re-enabled.
        """
        self._can_clear = False

    def sorted(self, key: typing.Any = None, reverse: bool = False):
        """Returns a newly constructed UniqueList containing the same items
        but sorted using the items themselves.

        Implementation:
            Internally, sorting is performed with list.sort(), with optional
            key and reverse arguments.
        """
        copied = self._items.copy()
        if key is not None:
            copied.sort(key=key, reverse=reverse)
        else:
            copied.sort(reverse=reverse)
        new_list = UniqueList[_T]()
        for item in copied:
            new_list.add(item)
        return new_list

    def __repr__(self) -> str:
        """Formats all items on this UniqueList into a string via repr(item).
        """
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

    def _validate_item(self, item: typing.Any) -> None:
        """
        Validates the type of the item.
        Important:
            As of Python 3.11, self.__orig_class__ is not assigned until after 
            __init__() has exited. Thus, use of this function has no effect if
            the caller is __init__().
        """
        if self._typecheck is False:
            return
        if self._typecheck is True:
            try:
                expected_type = self.__orig_class__.__args__[0]
            except:
                return
            if not isinstance(item, expected_type):
                raise self.ItemTypeException(item, type(item), str(item))
        elif isinstance(self._typecheck, type) or issubclass(type(self._typecheck), Protocol):
            expected_type = self._typecheck
            if not isinstance(item, expected_type):
                raise self.ItemTypeException(item, type(item), str(item))
        elif type(self._typecheck) == tuple:
            expected_type_tups = self._typecheck
            if not isinstance(item, expected_type_tups):
                raise self.ItemTypeException(item, type(item), str(item))
        elif callable(self._typecheck):
            if not self._typecheck(item):
                raise self.ItemTypeException(item, type(item), str(item))
        else:
            return


    class UniqueListException(Exception):
        _args: Sequence[typing.Any]
        _kwargs: Mapping[str, typing.Any]
        def __init__(self, *args, **kwargs) -> None:
            self._args = args
            self._kwargs = kwargs
            super().__init__(self._args, self._kwargs)

    class BadIndexException(UniqueListException):
        EXC_MESSAGE = "UniqueList: bad index."
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*[self.EXC_MESSAGE, *args], **kwargs)

    class ItemTypeException(UniqueListException):
        EXC_MESSAGE = "UniqueList: bad item type."
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*[self.EXC_MESSAGE, *args], **kwargs)

    class InvalidClearOperationException(UniqueListException):
        EXC_MESSAGE = "UniqueList: clear() has been disabled on this list."
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*[self.EXC_MESSAGE, *args], **kwargs)
