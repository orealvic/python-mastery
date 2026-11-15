"""2.04 — Dunder Methods & Properties

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 2.04` from the course root to test your work.
"""
from __future__ import annotations

import functools
import math
from typing import Iterator


class Vector:
    """An immutable-by-convention 2D vector.

    - `Vector(x, y)` stores `x` and `y`.
    - `repr(v)` -> "Vector(1, 2)" (use `!r` on each coordinate);
      `str(v)` -> "(1, 2)".
    - `==` compares coordinates (and returns NotImplemented for non-Vectors);
      equal vectors have equal hashes, so Vectors work in sets and as dict keys.
    - `v + w`, `v - w` -> new Vector; `-v` -> negated Vector.
    - `v * k` and `k * v` with a number `k` -> scaled Vector (support both orders).
    - `abs(v)` -> magnitude (Euclidean length) as a float.
    - `bool(v)` is False only for the zero vector.
    - Iterating yields `x` then `y`, so `x, y = v` works.

    >>> v = Vector(3, 4)
    >>> v + Vector(1, 1)
    Vector(4, 5)
    >>> 2 * v
    Vector(6, 8)
    >>> abs(v)
    5.0
    >>> x, y = v
    """

    def __init__(self, x: float, y: float):
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    def __add__(self, other: Vector) -> Vector:
        raise NotImplementedError

    def __sub__(self, other: Vector) -> Vector:
        raise NotImplementedError

    def __neg__(self) -> Vector:
        raise NotImplementedError

    def __mul__(self, k: float) -> Vector:
        raise NotImplementedError

    __rmul__ = __mul__

    def __abs__(self) -> float:
        raise NotImplementedError

    def __bool__(self) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[float]:
        raise NotImplementedError


@functools.total_ordering
class Money:
    """An amount of money stored as an integer number of cents.

    - `Money(cents, currency="USD")` stores `cents` (int) and `currency` (str).
    - `str(m)` -> "12.34 USD"; negative amounts put the sign first: "-5.50 USD".
    - `repr(m)` -> "Money(1234, 'USD')".
    - `Money.parse("12.34 EUR")` (classmethod) builds a Money from text:
      "<amount>" or "<amount> <CUR>"; the currency defaults to USD; the amount
      may be negative and has at most 2 decimals ("5" and "5.5" are fine).
      Invalid text raises ValueError. Do the arithmetic with integers
      (no float rounding!).
    - `==` and `hash` use (cents, currency).
    - `+`/`-` with another Money of the SAME currency -> new Money; a
      different currency raises ValueError.
    - `m * n` / `n * m` with an int `n` -> new Money.
    - `<`, `<=`, `>`, `>=` between same-currency Money (different currency
      raises ValueError). Hint: `functools.total_ordering`.
    - `sum([Money(...), ...])` must work: `0 + m` is treated as `m`
      (implement `__radd__` accepting the int 0 only).

    >>> str(Money(1234))
    '12.34 USD'
    >>> Money.parse("5.5 EUR")
    Money(550, 'EUR')
    >>> Money(100) + Money(250)
    Money(350, 'USD')
    """

    def __init__(self, cents: int, currency: str = "USD"):
        raise NotImplementedError

    @classmethod
    def parse(cls, text: str) -> Money:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    def _check(self, other: Money) -> None:
        raise NotImplementedError

    def __lt__(self, other: Money) -> bool:
        raise NotImplementedError

    def __add__(self, other: Money) -> Money:
        raise NotImplementedError

    def __radd__(self, other: int) -> Money:
        raise NotImplementedError

    def __sub__(self, other: Money) -> Money:
        raise NotImplementedError

    def __mul__(self, n: int) -> Money:
        raise NotImplementedError

    __rmul__ = __mul__


class Playlist:
    """A named, ordered collection of song titles that behaves like a sequence.

    - `Playlist(name, songs=None)`: stores `name`; copies `songs` into a new
      list (the caller's list must not be shared).
    - `len(p)` is the number of songs; an empty playlist is falsy.
    - `p[i]` returns a song (negative indexes work); `p[a:b]` returns a plain
      `list` of songs. (Delegate to the internal list.)
    - Iterating (`for s in p`) yields the songs in order, and can be repeated.
    - `"title" in p` tests membership.
    - `p.add(song)` appends and returns None.
    - `p + q` -> NEW Playlist named like `p` containing p's songs then q's.
    - `==` compares name and songs (non-Playlists -> NotImplemented).
    - `repr(p)` -> "Playlist('Road Trip', 3 songs)" (always the plural "songs").

    >>> p = Playlist("Mix", ["a", "b"])
    >>> len(p), p[0], "b" in p
    (2, 'a', True)
    >>> p
    Playlist('Mix', 2 songs)
    """

    def __init__(self, name: str, songs: list[str] | None = None):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError

    def __contains__(self, song: object) -> bool:
        raise NotImplementedError

    def add(self, song: str) -> None:
        raise NotImplementedError

    def __add__(self, other: Playlist) -> Playlist:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    __hash__ = None  # mutable container: unhashable

    def __repr__(self) -> str:
        raise NotImplementedError


class Temperature:
    """A temperature stored internally in Celsius, with validated properties.

    - `Temperature(celsius)`: goes through the `celsius` setter.
    - Property `celsius` (read/write): assigning a value below -273.15
      raises ValueError (exactly -273.15 is allowed).
    - Property `fahrenheit` (read/write): F = C * 9/5 + 32; assigning converts
      back to Celsius (and is validated the same way).
    - Property `kelvin` (READ-ONLY): C + 273.15. Assigning raises AttributeError.
    - Classmethod `from_fahrenheit(f)` builds a Temperature from Fahrenheit.
    - Staticmethod `c_to_f(c)` converts a plain number (no instance needed).
    - `repr(t)` -> "Temperature(25)" i.e. `Temperature(<celsius!r>)`.

    >>> t = Temperature(100)
    >>> t.fahrenheit
    212.0
    >>> t.fahrenheit = 32
    >>> t.celsius
    0.0
    """

    ABSOLUTE_ZERO = -273.15

    def __init__(self, celsius: float):
        raise NotImplementedError

    @property
    def celsius(self) -> float:
        raise NotImplementedError

    @celsius.setter
    def celsius(self, value: float) -> None:
        raise NotImplementedError

    @property
    def fahrenheit(self) -> float:
        raise NotImplementedError

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        raise NotImplementedError

    @property
    def kelvin(self) -> float:
        raise NotImplementedError

    @classmethod
    def from_fahrenheit(cls, f: float) -> Temperature:
        raise NotImplementedError

    @staticmethod
    def c_to_f(c: float) -> float:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


@functools.total_ordering
class Version:
    """A semantic version `major.minor.patch` (three non-negative ints).

    - `Version(major, minor, patch)`; attributes with those names.
    - `Version.parse("1.2.3")` (classmethod); anything that is not exactly three
      dot-separated non-negative integers raises ValueError.
    - `Version.is_valid("1.2.3")` (staticmethod) -> bool, never raises.
    - `str(v)` -> "1.2.3"; `repr(v)` -> "Version(1, 2, 3)".
    - Ordering compares (major, minor, patch) numerically ("1.10.0" > "1.9.0").
    - `==`/hash use the three numbers; comparing with a non-Version gives
      NotImplemented (so `Version(1,0,0) == "1.0.0"` is False).

    >>> Version.parse("1.10.0") > Version.parse("1.9.0")
    True
    >>> Version.is_valid("1.2")
    False
    """

    def __init__(self, major: int, minor: int, patch: int):
        raise NotImplementedError

    @classmethod
    def parse(cls, text: str) -> Version:
        raise NotImplementedError

    @staticmethod
    def is_valid(text: str) -> bool:
        raise NotImplementedError

    def _key(self) -> tuple[int, int, int]:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __lt__(self, other: Version) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError
