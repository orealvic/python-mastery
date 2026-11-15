"""Reference solutions for 3.07. Try the exercises yourself first!"""
import math
from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class Circle:
    radius: float


@dataclass(frozen=True)
class Rect:
    width: float
    height: float


@dataclass(frozen=True)
class Triangle:
    base: float
    height: float


@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    left: object
    right: object


@dataclass(frozen=True)
class Mul:
    left: object
    right: object


@dataclass(frozen=True)
class Neg:
    operand: object


class Light(Enum):
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    FLASHING = auto()


def classify(value) -> str:
    match value:
        case None:
            return "none"
        case bool():            # before int(): bool is a subclass of int
            return "bool"
        case 0:
            return "zero"
        case int():
            return "int"
        case float():
            return "float"
        case "":
            return "empty string"
        case str():
            return "string"
        case [] | ():
            return "empty sequence"
        case list() | tuple():
            return "sequence"
        case dict():
            return "dict"
        case _:
            return "other"


def parse_command(line: str) -> tuple:
    match line.split():
        case []:
            return ("noop",)
        case ["quit" | "exit"]:
            return ("quit",)
        case ["go", ("north" | "south" | "east" | "west") as direction]:
            return ("move", direction)
        case ["take", *items] if items:
            return ("take", items)
        case ["say", *words] if words:
            return ("say", " ".join(words))
        case _:
            return ("unknown", line)


def summarize_seq(seq) -> tuple:
    match seq:
        case str() | bytes() | bytearray():
            return ("not a sequence",)
        case []:
            return ("empty",)
        case [x]:
            return ("one", x)
        case [x, y]:
            return ("pair", x, y)
        case [first, *middle, last]:
            return ("many", first, last, len(middle))
        case _:
            return ("not a sequence",)


def area(shape) -> float:
    match shape:
        case Circle(r):
            return math.pi * r ** 2
        case Rect(w, h):
            return w * h
        case Triangle(base, height):
            return base * height / 2
        case _:
            raise TypeError(f"not a shape: {shape!r}")


def shape_name(shape) -> str:
    match shape:
        case Circle():
            return "circle"
        case Rect(w, h) if w == h:
            return "square"
        case Rect():
            return "rectangle"
        case Triangle():
            return "triangle"
        case _:
            return "unknown"


def handle_event(event) -> str:
    match event:
        case {"type": "click", "pos": (x, y)}:
            return f"click at {x},{y}"
        case {"type": "key", "key": k, "mods": [_, *_] as mods}:
            return "+".join([*mods, k])
        case {"type": "key", "key": k}:
            return f"key {k}"
        case {"type": "error", **rest}:
            return f"error with {len(rest)} detail(s)"
        case _:
            return "ignored"


def parse_config(cfg) -> tuple:
    match cfg:
        case {"mode": "tcp", "host": str() as host, "port": int() as port} \
                if not isinstance(port, bool) and 1 <= port <= 65535:
            return ("tcp", host, port)
        case {"mode": "unix", "path": str() as path}:
            return ("unix", path)
        case _:
            raise ValueError(f"invalid config: {cfg!r}")


def evaluate(expr, env: dict | None = None):
    env = env or {}
    match expr:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return evaluate(left, env) + evaluate(right, env)
        case Mul(left, right):
            return evaluate(left, env) * evaluate(right, env)
        case Neg(operand):
            return -evaluate(operand, env)
        case _:
            raise TypeError(f"unknown node: {expr!r}")


def simplify(expr):
    match expr:
        case Add(left, right):
            match (simplify(left), simplify(right)):
                case (Num(a), Num(b)):
                    return Num(a + b)
                case (Num(0), x) | (x, Num(0)):
                    return x
                case (l, r):
                    return Add(l, r)
        case Mul(left, right):
            match (simplify(left), simplify(right)):
                case (Num(a), Num(b)):
                    return Num(a * b)
                case (Num(0), _) | (_, Num(0)):
                    return Num(0)
                case (Num(1), x) | (x, Num(1)):
                    return x
                case (l, r):
                    return Mul(l, r)
        case Neg(operand):
            match simplify(operand):
                case Num(n):
                    return Num(-n)
                case Neg(inner):
                    return inner
                case x:
                    return Neg(x)
        case _:
            return expr


def next_light(light: Light) -> Light:
    match light:
        case Light.RED:
            return Light.GREEN
        case Light.GREEN:
            return Light.YELLOW
        case Light.YELLOW:
            return Light.RED
        case Light.FLASHING:
            return Light.FLASHING
        case _:
            raise ValueError(f"not a Light: {light!r}")


def flatten(data) -> list:
    match data:
        case str() | bytes():
            return [data]
        case [*items]:
            return [leaf for item in items for leaf in flatten(item)]
        case dict():
            return [leaf for item in data.values() for leaf in flatten(item)]
        case _:
            return [data]


class Vec:
    __match_args__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Vec({self.x!r}, {self.y!r})"


def quadrant(p) -> str:
    match p:
        case Vec(0, 0) | (0, 0):
            return "origin"
        case Vec(x, 0) | (x, 0):
            return "x-axis"
        case Vec(0, y) | (0, y):
            return "y-axis"
        case Vec(x, y) | (x, y) if x > 0 and y > 0:
            return "I"
        case Vec(x, y) | (x, y) if x < 0 and y > 0:
            return "II"
        case Vec(x, y) | (x, y) if x < 0 and y < 0:
            return "III"
        case Vec(x, y) | (x, y) if x > 0 and y < 0:
            return "IV"
        case _:
            raise ValueError(f"not a point: {p!r}")
