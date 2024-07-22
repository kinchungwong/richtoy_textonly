from abc import ABC, abstractmethod
from collections.abc import Mapping, Iterable, MutableSet
from typing import ForwardRef, Optional


IntIntMultimap = ForwardRef("IntIntMultimap")
_KeyType = int
_ValueType = int
_KeyValuePair = tuple[_KeyType, _ValueType]
_DictView = ForwardRef("_DictView")
_PairSetView = ForwardRef("_PairSetView")


class _IIMM_Mutator(ABC):
    @abstractmethod
    def _get_vs_else_none(self, key: _KeyType) -> Optional[set[_ValueType]]:
        pass

    @abstractmethod
    def _add_kv_return_vs(self, key: _KeyType, value: _ValueType) -> set[_ValueType]:
        pass

    @abstractmethod
    def _rm_kv_return_vs(self, key: _KeyType, value: _ValueType) -> Optional[set[_ValueType]]:
        pass

    @abstractmethod
    def _get_dict(self) -> dict[_KeyType, set[_ValueType]]:
        pass

    @abstractmethod
    def keys(self) -> Iterable[_KeyType]:
        pass

    @property
    @abstractmethod
    def total(self) -> int:
        pass


class _ValueSet(MutableSet[_ValueType]):
    _owner: _IIMM_Mutator
    _key: _KeyType
    _values: Optional[set[int]]

    def __init__(self, owner: _IIMM_Mutator, key: _KeyType) -> None:
        self._owner = owner
        self._key = key
        self._values = owner._get_vs_else_none(key)

    def __contains__(self, value: _ValueType) -> bool:
        if self._values is None:
            self._values = self._owner._get_vs_else_none(self._key)
        if self._values is None:
            return False
        return value in self._values

    def __iter__(self) -> Iterable[_ValueType]:
        if self._values is None:
            self._values = self._owner._get_vs_else_none(self._key)
        yield from self._values

    def __len__(self) -> int:
        if self._values is None:
            self._values = self._owner._get_vs_else_none(self._key)
        return len(self._values)

    def add(self, value: _ValueType) -> None:
        self._values = self._owner._add_kv_return_vs(self._key, value)

    def discard(self, value: _ValueType):
        self._values = self._owner._rm_kv_return_vs(self._key, value)


class _DictView(Mapping[_KeyType, _ValueSet]):
    _owner: _IIMM_Mutator

    def __init__(self, owner: _IIMM_Mutator) -> None:
        self._owner = owner
    
    def __getitem__(self, key: _KeyType) -> _ValueSet:
        return _ValueSet(self._owner, key)
    
    def __iter__(self) -> Iterable[_KeyType]:
        yield from self._get_dict().keys()

    def __len__(self):
        return len(self._get_dict())

    def _get_dict(self):
        return self._owner._get_dict()

    def __contains__(self, key: _KeyType) -> bool:
        return key in self._get_dict()


class _PairSetView(MutableSet[_KeyValuePair]):
    _owner: _IIMM_Mutator

    def __init__(self, owner: _IIMM_Mutator) -> None:
        self._owner = owner

    def __contains__(self, key_value: _KeyValuePair) -> bool:
        key = key_value[0]
        value = key_value[1]
        vs = self._owner._get_vs_else_none(key)
        if vs is None:
            return False
        return value in vs

    def __iter__(self) -> Iterable[_KeyValuePair]:
        _keys = tuple(self._owner.keys())
        for key in _keys:
            vs = self._owner._get_vs_else_none(key)
            if vs is None:
                continue
            for value in vs:
                yield (key, value)

    def __len__(self) -> int:
        return self._owner.total
        
    def add(self, key_value: _KeyValuePair) -> None:
        self._owner._add_kv_return_vs(key_value[0], key_value[1])

    def discard(self, key_value: _KeyValuePair) -> None:
        self._owner._rm_kv_return_vs(key_value[0], key_value[1])


class IntIntMultimap(_IIMM_Mutator):
    _dict: dict[_KeyType, set[_ValueType]]
    _total: int
    _psv: _PairSetView
    _dv: _DictView

    def __init__(
        self,
        /,
        _internal_from: IntIntMultimap = None,
    ) -> None:
        if _internal_from is not None:
            assert isinstance(_internal_from, IntIntMultimap)
            self._dict = _internal_from._dict.copy()
            self._total = _internal_from._total
        else:
            self._dict = dict() 
            self._total = 0
            pass
        self._psv = _PairSetView(self)
        self._dv = _DictView(self)

    def keys(self) -> Iterable[_KeyType]:
        return self._dict.keys()

    @property
    def total(self) -> int:
        return self._total

    def clear(self) -> None:
        self._dict.clear()
        self._total = 0

    def copy(self):
        return IntIntMultimap(_internal_from=self)

    def __getitem__(self, key: _KeyType) -> _ValueSet:
        return _ValueSet(self, key)
    
    def items(self) -> _PairSetView:
        return self._psv
    
    def value_sets(self) -> _DictView:
        return self._dv
    
    def __iter__(self) -> Iterable[_KeyValuePair]:
        yield from self._psv

    def add(self, key: _KeyType, value: _ValueType) -> bool:
        """Adds the (key, value) to the multimap.
        Returns:
            True if a new value is added.
            False if the (key, value) was already present.
        """
        old_total = self._total
        self._add_kv_return_vs(key, value)
        return self._total > old_total

    def discard(self, key: _KeyType, value: _ValueType) -> bool:
        """Removes  the (key, value) to the multimap.

        Returns:
            True if the (key, value) was already present, and therefore removed.
            False if the (key, value) was not present.
        """
        old_total = self._total
        self._rm_kv_return_vs(key, value)
        return self._total < old_total

    def _get_vs_else_none(self, key: _KeyType) -> Optional[set[_ValueType]]:
        return self._dict.get(key, default=None)

    def _add_kv_return_vs(self, key: _KeyType, value: _ValueType) -> set[_ValueType]:
        if key not in self._dict:
            self._dict[key] = set[_ValueType]()
        if value not in self._dict[key]:
            self._dict[key].add(value)
            self._total += 1
        return self._dict[key]

    def _rm_kv_return_vs(self, key: _KeyType, value: _ValueType) -> Optional[set[_ValueType]]:
        if key not in self._dict:
            return None
        if value in self._dict[key]:
            self._dict[key].discard(value)
            self._total -= 1
        if len(self._dict[key]) > 0:
            return self._dict[key]
        self._dict.pop(key)
        return None

    def _get_dict(self) -> dict[_KeyType, set[_ValueType]]:
        return self._dict
