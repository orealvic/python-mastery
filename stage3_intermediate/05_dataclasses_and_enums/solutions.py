"""Reference solutions for 3.05. Try the exercises yourself first!"""
import math
from dataclasses import MISSING, dataclass, field, fields, is_dataclass, replace
from enum import Enum, Flag, IntEnum, StrEnum, auto


@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass
class Product:
    name: str
    price: float
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name must not be empty")
        if self.price < 0:
            raise ValueError("price must be >= 0")


@dataclass(kw_only=True, slots=True)
class ServerConfig:
    host: str
    port: int = 8080
    debug: bool = False

    def __post_init__(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError(f"invalid port {self.port}")


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("dimensions must be positive")
        self.area = self.width * self.height


def with_changes(obj, **changes):
    if not is_dataclass(obj) or isinstance(obj, type):
        raise TypeError("obj must be a dataclass instance")
    return replace(obj, **changes)


def non_default_fields(obj) -> dict:
    result = {}
    for f in fields(obj):
        value = getattr(obj, f.name)
        if f.default is not MISSING:
            default = f.default
        elif f.default_factory is not MISSING:
            default = f.default_factory()
        else:
            result[f.name] = value
            continue
        if value != default:
            result[f.name] = value
    return result


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
    return day in (Weekday.SATURDAY, Weekday.SUNDAY)


def parse_weekday(text: str) -> Weekday:
    cleaned = text.strip()
    if cleaned.isdigit():
        return Weekday(int(cleaned))
    try:
        return Weekday[cleaned.upper()]
    except KeyError:
        raise ValueError(f"not a weekday: {text!r}") from None


def describe_permissions(p: Permission) -> str:
    names = [m.name for m in Permission if m in p]
    return "|".join(names) if names else "NONE"


def make_level_enum() -> type:
    class Level(StrEnum):
        LOW = auto()
        MEDIUM = auto()
        HIGH = auto()

    return Level


def make_priority_enum() -> type:
    class Priority(IntEnum):
        LOW = auto()
        MEDIUM = auto()
        HIGH = auto()

    return Priority
