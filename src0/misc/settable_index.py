import builtins
from collections.abc import Sequence, Mapping
import typing
from typing import Union, ForwardRef


SettableIndex = ForwardRef("SettableIndex")

class SettableIndex:
    _value: int

    def __init__(self, value: int = -1) -> None:
        self._value = value

    def set(self, value: int):
        if value < 0:
            raise self.BadValue(new_value=value)
        if self._value >= 0 and self._value != value:
            raise self.ValueConflict(old_value=self._value, new_value=value)
        self._value = value

    def has_value(self) -> bool:
        return self._value >= 0

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name == "value":
            self.set(value)
        else:
            super().__setattr__(name, value)
    
    @property
    def value(self) -> int:
        return self._value

    def __int__(self) -> int:
        if self._value < 0:
            raise self.ValueNotSet()
        return self._value

    def __repr__(self) -> str:
        if self._value >= 0:
            return str(self._value)
        else:
            return "NotSet"

    def __hash__(self) -> int:
        return builtins.hash(builtins.id(self)) ^ builtins.hash(self._value)

    def __eq__(self, other: Union[SettableIndex, int]) -> bool:
        if self is other:
            return True
        if isinstance(other, SettableIndex):
            return self._value == other._value
        elif type(other) == int:
            return self._value == other
        else:
            return False

    class SettableIndexExeption(Exception):
        _args: Sequence[typing.Any]
        _kwargs: Mapping[str, typing.Any]
        def __init__(self, *args, **kwargs) -> None:
            self._args = args
            self._kwargs = kwargs
            super().__init__(self._args, self._kwargs)

    class BadValue(SettableIndexExeption):
        pass

    class ValueNotSet(SettableIndexExeption):
        pass

    class ValueConflict(SettableIndexExeption):
        pass
