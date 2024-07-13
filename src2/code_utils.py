from typing import Protocol, NamedTuple


class Vec2i(NamedTuple):
    x: int
    y: int

class Vec3i(NamedTuple):
    x: int
    y: int
    z: int

class Vec2f(NamedTuple):
    x: float
    y: float

class Vec3f(NamedTuple):
    x: float
    y: float
    z: float

class HasIndex(Protocol):
    INDEX_NOT_INITIALIZED = -1
    index: int

class HasTaggedIndex(HasIndex, Protocol):
    @property
    def tagged_index(self) -> tuple[type, int]:
        return (self.__class__, self.index)
