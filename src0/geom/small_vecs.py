from typing import NamedTuple


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

class Size2i(NamedTuple):
    width: int
    height: int

class Size2f(NamedTuple):
    width: float
    height: float

class Rect2i(NamedTuple):
    x: int
    y: int
    width: int
    height: int

class Rect2f(NamedTuple):
    x: float
    y: float
    width: float
    height: float

class Box2i(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

class Box2f(NamedTuple):
    left: float
    top: float
    right: float
    bottom: float
