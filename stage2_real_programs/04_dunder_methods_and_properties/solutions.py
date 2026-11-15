"""Reference solutions for 2.04. Try the exercises yourself first!"""
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
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: Vector) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __mul__(self, k: float) -> Vector:
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return bool(self.x or self.y)

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y


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
        self.cents = cents
        self.currency = currency

    @classmethod
    def parse(cls, text: str) -> Money:
        parts = text.split()
        if len(parts) not in (1, 2):
            raise ValueError(f"invalid money: {text!r}")
        amount = parts[0]
        currency = parts[1] if len(parts) == 2 else "USD"
        sign = -1 if amount.startswith("-") else 1
        digits = amount[1:] if sign < 0 else amount
        whole, _, frac = digits.partition(".")
        if not whole.isdigit() or (frac and not frac.isdigit()) or len(frac) > 2:
            raise ValueError(f"invalid money: {text!r}")
        cents = int(whole) * 100 + int(frac.ljust(2, "0") or "0")
        return cls(sign * cents, currency)

    def __str__(self) -> str:
        sign = "-" if self.cents < 0 else ""
        whole, frac = divmod(abs(self.cents), 100)
        return f"{sign}{whole}.{frac:02d} {self.currency}"

    def __repr__(self) -> str:
        return f"Money({self.cents!r}, {self.currency!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    def __hash__(self) -> int:
        return hash((self.cents, self.currency))

    def _check(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"currency mismatch: {self.currency} vs {other.currency}")

    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self.cents < other.cents

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.cents + other.cents, self.currency)

    def __radd__(self, other: int) -> Money:
        if other == 0:
            return self
        return NotImplemented

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, n: int) -> Money:
        if not isinstance(n, int):
            return NotImplemented
        return Money(self.cents * n, self.currency)

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
        self.name = name
        self._songs = list(songs or [])

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self._songs)

    def __contains__(self, song: object) -> bool:
        return song in self._songs

    def add(self, song: str) -> None:
        self._songs.append(song)

    def __add__(self, other: Playlist) -> Playlist:
        if not isinstance(other, Playlist):
            return NotImplemented
        return Playlist(self.name, self._songs + other._songs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Playlist):
            return NotImplemented
        return (self.name, self._songs) == (other.name, other._songs)

    __hash__ = None  # mutable container: unhashable

    def __repr__(self) -> str:
        return f"Playlist({self.name!r}, {len(self)} songs)"


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
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < self.ABSOLUTE_ZERO:
            raise ValueError(f"below absolute zero: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self.c_to_f(self._celsius)

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    @classmethod
    def from_fahrenheit(cls, f: float) -> Temperature:
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def c_to_f(c: float) -> float:
        return c * 9 / 5 + 32

    def __repr__(self) -> str:
        return f"Temperature({self._celsius!r})"


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
        self.major = major
        self.minor = minor
        self.patch = patch

    @classmethod
    def parse(cls, text: str) -> Version:
        parts = text.split(".")
        if len(parts) != 3 or not all(p.isascii() and p.isdigit() for p in parts):
            raise ValueError(f"invalid version: {text!r}")
        return cls(*map(int, parts))

    @staticmethod
    def is_valid(text: str) -> bool:
        try:
            Version.parse(text)
        except ValueError:
            return False
        return True

    def _key(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __str__(self) -> str:
        return ".".join(map(str, self._key()))

    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())
