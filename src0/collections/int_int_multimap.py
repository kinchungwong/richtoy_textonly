from collections.abc import Sequence, Mapping, Iterable
import typing
from typing import Union


class IntIntMultimap:
    _data: dict[int, Union[int, set[int]]]
    _total: int
    
    def __init__(self) -> None:
        self._data = dict()
        self._total = 0

    def add(self, key: int, value: int) -> bool:
        """Inserts (key, value) into the multimap.
        
        Returns:
            True if the (key, value) was not originally present and therefore
            was inserted.
            False if the (key, value) was originally present and therefore
            left unchanged.
        """
        if type(key) != int:
            raise TypeError(key)
        if type(value) != int:
            raise TypeError(value)
        if key not in self._data:
            self._data[key] = value
            self._total += 1
            return True
        orig_value = self._data[key]
        t = type(orig_value)
        if t == int:
            if value == orig_value:
                return False
            self._data[key] = set((orig_value, value))
            self._total += 1
            return True
        elif t == set:
            if value in orig_value:
                return False
            orig_value.add(value)
            self._total += 1
            return True
        else:
            raise self.ImplementationError()

    def __contains__(self, key: int) -> bool:
        """Checks if the key is present.
        """
        if type(key) != int:
            return False
        if key not in self._data:
            return False
        orig_value = self._data[key]
        t = type(orig_value)
        if t == int:
            return True
        elif t == set:
            return len(orig_value) > 0
        else:
            raise self.ImplementationError()

    def contains_item(self, key: int, value: int) -> bool:
        """Removes the specific (key, value) from the multimap.

        Returns:
            True if the specific (key, value) was originally present and 
            therefore removed.
            False if the specific (key, value) was originally not present.
        """
        if type(key) != int:
            raise TypeError(key)
        if type(value) != int:
            raise TypeError(value)
        if key not in self._data:
            return False
        orig_value = self._data[key]
        t = type(orig_value)
        if t == int:
            return orig_value == value
        elif t == set:
            return value in orig_value
        else:
            raise self.ImplementationError()

    def remove_item(self, key: int, value: int) -> bool:
        """Removes the specific (key, value) from the multimap.

        Returns:
            True if the specific (key, value) was originally present and 
            therefore removed.
            False if the specific (key, value) was originally not present.
        """
        if type(key) != int:
            raise TypeError(key)
        if type(value) != int:
            raise TypeError(value)
        if key not in self._data:
            return False
        orig_value = self._data[key]
        t = type(orig_value)
        if t == int:
            if orig_value != value:
                return False
            self._data.pop(key)
            self._total -= 1
            return True
        elif t == set:
            if value not in orig_value:
                return False
            orig_value.remove(value)
            if len(orig_value) == 0:
                self._data.pop(key)
            self._total -= 1
            return True
        else:
            raise self.ImplementationError()

    def __getitem__(self, key: int) -> Iterable[int]:
        """Retrieves all values associated with the specified key.
        """
        if type(key) != int:
            raise TypeError(key)
        if key not in self._data:
            return
        orig_value = self._data[key]
        t = type(orig_value)
        if t == int:
            yield orig_value
        elif t == set:
            yield from orig_value
        else:
            raise self.ImplementationError()

    def __len__(self) -> int:
        return self._total

    def keys(self) -> Iterable[int]:
        """Iterates through all keys.
        Remark:
            To iterate through all key-value pairs, use items() instead.
        """
        yield from self._data.keys()

    def __iter__(self):
        yield from self.items()

    def items(self) -> Iterable[tuple[int, int]]:
        """Iterates through all key-value pairs.

        Remark:
            To iterate through keys only, use __iter__() instead.
        """
        for key, orig_value in self._data.items():
            t = type(orig_value)
            if t == int:
                yield (key, orig_value)
            elif t == set:
                for value in orig_value:
                    yield (key, value)
            else:
                raise self.ImplementationError()

    def clear(self) -> None:
        self._data = dict()
        self._total = 0

    def copy(self):
        other = IntIntMultimap()
        other._data = self._data.copy()
        other._total = self._total
        return other


    class IntIntMultimapException(Exception):
        pass

    class ImplementationError(IntIntMultimapException):
        pass
