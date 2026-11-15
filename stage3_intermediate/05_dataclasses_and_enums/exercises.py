"""3.05 — Dataclasses & Enums

Replace each stub with a real implementation. For the classes below, delete
the placeholder `__init__` and turn them into proper @dataclass definitions
with the options described in each docstring.
Run `python check.py 3.05` from the course root to test your work.
"""
from dataclasses import dataclass, field, fields, replace, asdict, is_dataclass
from enum import Enum, IntEnum, StrEnum, Flag, auto


# ---- Dataclass exercises -----------------------------------------------------

class Point:
    """Make this an immutable, orderable, hashable 2-D point:

        @dataclass(frozen=True, order=True)  with fields x: float, y: float

    Also add a method `distance_to(self, other: "Point") -> float` returning
    the Euclidean distance.

    >>> Point(0, 0).distance_to(Point(3, 4))
    5.0
    >>> sorted([Point(2, 1), Point(1, 5)])[0]
    Point(x=1, y=5)
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Product:
    """Make this a dataclass with fields:

        name: str
        price: float
        tags: list[str]   (default: a NEW empty list per instance)

    `__post_init__` must:
      * strip surrounding whitespace from `name`; raise ValueError if the
        stripped name is empty
      * raise ValueError if price < 0

    >>> Product("  Pen ", 1.5)
    Product(name='Pen', price=1.5, tags=[])
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class ServerConfig:
    """Make this a keyword-only, slotted dataclass:

        @dataclass(kw_only=True, slots=True)
        fields: host: str            (required)
                port: int = 8080
                debug: bool = False

    __post_init__ raises ValueError unless 1 <= port <= 65535.

    >>> ServerConfig(host="localhost")
    ServerConfig(host='localhost', port=8080, debug=False)
    >>> ServerConfig("localhost")      # TypeError: keyword-only
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Rectangle:
    """Make this a dataclass with fields width: float, height: float and a
    derived field `area: float` declared with field(init=False, repr=False,
    compare=False) that __post_init__ computes as width * height.
    __post_init__ raises ValueError if width <= 0 or height <= 0.

    >>> r = Rectangle(2, 3)
    >>> r.area
    6
    >>> r
    Rectangle(width=2, height=3)
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


def with_changes(obj, **changes):
    """Return a COPY of the dataclass instance `obj` with the given fields
    replaced (works for frozen dataclasses). Do not modify `obj`.
    Raise TypeError if `obj` is not a dataclass instance.

    Hint: dataclasses.replace / is_dataclass.
    """
    raise NotImplementedError


def non_default_fields(obj) -> dict:
    """Return {field_name: value} for every field of dataclass instance `obj`
    whose current value differs from that field's default (default or
    default_factory()). Fields with no default are always included.
    Use dataclasses.fields(); compare with !=. MISSING is
    dataclasses.MISSING.

    >>> non_default_fields(ServerConfig(host="h", port=9000))   # doctest: +SKIP
    {'host': 'h', 'port': 9000}
    """
    raise NotImplementedError


# ---- Enum exercises ----------------------------------------------------------

class Weekday(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


def is_weekend(day: Weekday) -> bool:
    """True for Saturday and Sunday.

    >>> is_weekend(Weekday.SUNDAY), is_weekend(Weekday.MONDAY)
    (True, False)
    """
    raise NotImplementedError


def parse_weekday(text: str) -> Weekday:
    """Convert a case-insensitive name ("friday", " FRIDAY ") or a numeric
    string ("5") to a Weekday. Raise ValueError for anything else.

    >>> parse_weekday("friday")
    <Weekday.FRIDAY: 5>
    """
    raise NotImplementedError


def describe_permissions(p: Permission) -> str:
    """Return member names joined with "|" in definition order, or "NONE"
    if no flags are set.

    >>> describe_permissions(Permission.READ | Permission.EXECUTE)
    'READ|EXECUTE'
    >>> describe_permissions(Permission(0))
    'NONE'
    """
    raise NotImplementedError


def make_level_enum() -> type:
    """Create and return a StrEnum class named "Level" with members
    LOW, MEDIUM, HIGH whose values are "low", "medium", "high"
    (use auto() or explicit strings). Members must be str instances:
    Level.LOW == "low".

    You may define the class inside this function or use the functional API.
    """
    raise NotImplementedError


def make_priority_enum() -> type:
    """Create and return an IntEnum class named "Priority" with members
    LOW=1, MEDIUM=2, HIGH=3 (use auto()). Priorities compare as integers:
    Priority.HIGH > Priority.LOW.
    """
    raise NotImplementedError
