"""3.07 — Structural Pattern Matching

Replace each stub with a real implementation that uses `match` / `case`.
The dataclasses and enum below are provided: do not change them.
`Vec` is a class you must write yourself (see its docstring).
Run `python check.py 3.07` from the course root to test your work.
"""
import math
from dataclasses import dataclass
from enum import Enum, auto


# ---- Provided data types -----------------------------------------------------

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


# ---- Exercises ---------------------------------------------------------------

def classify(value) -> str:
    """Classify `value` with literal and type patterns. Return the first that fits:

        None                          -> "none"
        any bool                      -> "bool"
        0 or 0.0                      -> "zero"
        any other int                 -> "int"
        any float                     -> "float"
        ""                            -> "empty string"
        any other str                 -> "string"
        empty list or empty tuple     -> "empty sequence"
        any other list or tuple       -> "sequence"
        any dict                      -> "dict"
        anything else                 -> "other"

    >>> classify(True), classify(0), classify(7), classify(2.5)
    ('bool', 'zero', 'int', 'float')
    >>> classify([]), classify((1, 2)), classify({}), classify(b"x")
    ('empty sequence', 'sequence', 'dict', 'other')
    """
    raise NotImplementedError


def parse_command(line: str) -> tuple:
    """Parse a text-adventure command using sequence patterns on `line.split()`.

        ""  (or only whitespace)       -> ("noop",)
        "quit" or "exit"               -> ("quit",)
        "go <dir>"  (north/south/east/west only)   -> ("move", dir)
        "take <item> [<item> ...]"     -> ("take", [items...])     (a list)
        "say <word> [<word> ...]"      -> ("say", "words joined by single spaces")
        anything else                  -> ("unknown", line)        (the ORIGINAL line)

    "take" or "say" with nothing after them are unknown.

    >>> parse_command("go north")
    ('move', 'north')
    >>> parse_command("take lamp  sword")
    ('take', ['lamp', 'sword'])
    >>> parse_command("say hello   there")
    ('say', 'hello there')
    >>> parse_command("go up")
    ('unknown', 'go up')
    """
    raise NotImplementedError


def summarize_seq(seq) -> tuple:
    """Describe a list/tuple using sequence patterns with a star pattern.

        []                 -> ("empty",)
        [x]                -> ("one", x)
        [x, y]             -> ("pair", x, y)
        [first, ..., last] -> ("many", first, last, number_of_middle_items)

    Anything that is not a (non-string) sequence -> ("not a sequence",).

    >>> summarize_seq([])
    ('empty',)
    >>> summarize_seq((1, 2))
    ('pair', 1, 2)
    >>> summarize_seq([1, 2, 3, 4, 5])
    ('many', 1, 5, 3)
    >>> summarize_seq("abc")
    ('not a sequence',)
    """
    raise NotImplementedError


def area(shape) -> float:
    """Area of a Circle (pi * r**2), Rect (w * h) or Triangle (base * height / 2).
    Use class patterns with positional sub-patterns. Raise TypeError for
    any other object.

    >>> area(Rect(3, 4))
    12
    >>> area(Triangle(base=6, height=5))
    15.0
    """
    raise NotImplementedError


def shape_name(shape) -> str:
    """Name a shape using class patterns and a guard:

        Circle                      -> "circle"
        Rect with width == height   -> "square"
        any other Rect              -> "rectangle"
        Triangle                    -> "triangle"
        anything else               -> "unknown"

    >>> shape_name(Rect(2, 2)), shape_name(Rect(2, 3))
    ('square', 'rectangle')
    """
    raise NotImplementedError


def handle_event(event) -> str:
    """Describe a JSON-like event dict using mapping patterns.

        {"type": "click", "pos": (x, y)}   -> "click at X,Y"       (pos may be a list or tuple)
        {"type": "key", "key": k, "mods": [non-empty list]}
                                            -> modifiers and key joined with "+"
        {"type": "key", "key": k}           -> "key K"
        {"type": "error", ...}              -> "error with N detail(s)", where N is the number
                                               of keys OTHER than "type" (use **rest)
        anything else (including non-dicts) -> "ignored"

    Extra keys are allowed on click/key events.

    >>> handle_event({"type": "click", "pos": [3, 4]})
    'click at 3,4'
    >>> handle_event({"type": "key", "key": "k", "mods": ["ctrl", "shift"]})
    'ctrl+shift+k'
    >>> handle_event({"type": "key", "key": "k", "mods": []})
    'key k'
    >>> handle_event({"type": "error", "code": 500, "msg": "boom"})
    'error with 2 detail(s)'
    """
    raise NotImplementedError


def parse_config(cfg) -> tuple:
    """Validate a config dict with mapping patterns and return a normalised tuple.

        {"mode": "tcp", "host": str, "port": int with 1 <= port <= 65535}
                                      -> ("tcp", host, port)
        {"mode": "unix", "path": str} -> ("unix", path)

    Extra keys are ignored. Anything else (wrong mode, missing key, wrong type,
    port out of range, not a dict) raises ValueError.

    >>> parse_config({"mode": "tcp", "host": "localhost", "port": 8080})
    ('tcp', 'localhost', 8080)
    >>> parse_config({"mode": "unix", "path": "/tmp/s.sock", "debug": True})
    ('unix', '/tmp/s.sock')
    """
    raise NotImplementedError


def evaluate(expr, env: dict | None = None):
    """Evaluate an expression tree built from Num, Var, Add, Mul and Neg.
    `Var(name)` is looked up in `env` (KeyError if missing). Raise TypeError
    for any other node.

    >>> evaluate(Add(Num(1), Mul(Num(2), Var("x"))), {"x": 10})
    21
    >>> evaluate(Neg(Num(5)))
    -5
    """
    raise NotImplementedError


def simplify(expr):
    """Return a simplified COPY of an expression tree (nodes are immutable).
    Simplify children first, then apply these rules:

        Add(Num(a), Num(b))  -> Num(a + b)         Mul(Num(a), Num(b)) -> Num(a * b)
        Add(Num(0), x)       -> x   (either side)  Mul(Num(1), x)      -> x   (either side)
        Mul(Num(0), x)       -> Num(0)  (either side)
        Neg(Num(n))          -> Num(-n)            Neg(Neg(x))         -> x
        anything else is rebuilt unchanged (with simplified children)

    Num and Var are returned as they are.

    >>> simplify(Add(Num(0), Mul(Num(1), Var("x"))))
    Var(name='x')
    >>> simplify(Mul(Var("y"), Add(Num(2), Num(-2))))
    Num(value=0)
    """
    raise NotImplementedError


def next_light(light: Light) -> Light:
    """Traffic light cycle using value patterns (dotted enum names):
    RED -> GREEN -> YELLOW -> RED. FLASHING stays FLASHING.
    Raise ValueError for anything that is not a Light.

    >>> next_light(Light.RED)
    <Light.GREEN: 2>
    """
    raise NotImplementedError


def flatten(data) -> list:
    """Flatten arbitrarily nested lists, tuples and dicts (dict VALUES only, in order)
    into one list of leaves. Strings and bytes are leaves (do not split them).

    >>> flatten([1, [2, (3, "ab")], {"a": 4, "b": [5]}])
    [1, 2, 3, 'ab', 4, 5]
    >>> flatten("hi")
    ['hi']
    """
    raise NotImplementedError


class Vec:
    """Write a plain class (NOT a dataclass) for a 2-D vector:

      * `__init__(self, x, y)` stores `self.x` and `self.y`
      * a class attribute `__match_args__ = ("x", "y")` so that `Vec(a, b)` works
        as a positional class pattern
      * `__repr__` returning e.g. "Vec(1, 2)"

    >>> Vec(1, 2)
    Vec(1, 2)
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


def quadrant(p) -> str:
    """Locate a point given as a `Vec` OR a 2-tuple, using one OR pattern per case
    (e.g. `case Vec(x, y) | (x, y)`) plus guards:

        (0, 0)                    -> "origin"
        y == 0 (x non-zero)       -> "x-axis"
        x == 0 (y non-zero)       -> "y-axis"
        x > 0, y > 0              -> "I"
        x < 0, y > 0              -> "II"
        x < 0, y < 0              -> "III"
        x > 0, y < 0              -> "IV"

    Raise ValueError for anything that is not a Vec or 2-tuple.

    >>> quadrant(Vec(3, -1)), quadrant((-2, -2)), quadrant((0, 0))
    ('IV', 'III', 'origin')
    """
    raise NotImplementedError
