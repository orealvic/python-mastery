# 3.07 — Structural Pattern Matching

## Learning goals
- Read and write `match` / `case` statements (Python 3.10+)
- Use literal, capture, wildcard, and value (dotted-name) patterns
- Destructure sequences (with `*rest`) and mappings (with `**rest`)
- Match objects with class patterns, `__match_args__`, and dataclasses
- Combine patterns with `|`, bind with `as`, and filter with guards
- Know when a plain `if`/`elif` or a dict lookup is the better tool

## 1. It is not a C `switch`

`match` compares the *shape* of a value against patterns, top to bottom, and runs the first
`case` that fits. A pattern can also *bind names* as it matches.

```python
def http(status):
    match status:
        case 200:
            return "ok"
        case 404:
            return "not found"
        case 500 | 502 | 503:        # OR pattern
            return "server error"
        case _:                      # wildcard: matches anything, binds nothing
            return "other"

http(503)    # 'server error'
```

If no case matches and there is no `_`, nothing happens (no error).

## 2. Literal, capture, and value patterns

- Literals (`200`, `"go"`, `None`, `True`) match by equality (`None`/`True`/`False` by identity).
- A **bare name** is a *capture*: it always matches and binds. It is NOT a comparison!
- A **dotted name** (`Color.RED`, `http.HTTPStatus.OK`) is a *value pattern*: compared with `==`.

```python
RED = "red"
match "blue":
    case RED:            # captures! RED is now "blue"; this case always matches
        print("red?")
```

Fix: use a dotted name (put constants in an enum or class) or a literal. Because a capture
always matches, Python rejects an irrefutable case that is not last (`SyntaxError`).

```python
from enum import Enum

class Color(Enum):
    RED = 1; GREEN = 2

def label(c):
    match c:
        case Color.RED:   return "stop"
        case Color.GREEN: return "go"
```

## 3. Sequence patterns

`[...]` and `(...)` are interchangeable and match any sequence (list, tuple, `range`, ...)
of the right length, but never `str`, `bytes`, or `bytearray`. Use `*name` to capture the rest
as a list, `*_` to ignore it.

```python
def describe(seq):
    match seq:
        case []:                      return "empty"
        case [x]:                     return f"one: {x}"
        case [first, *_, last]:       return f"{first}..{last}"

describe([1, 2, 3, 4])   # '1..4'
describe((7,))           # 'one: 7'
describe("ab")           # falls through: strings are not sequences here -> None
```

Patterns nest: `case ["move", (x, y)]` matches `["move", [3, 4]]`.

## 4. Mapping patterns

`{key: pattern}` matches any mapping that *has* those keys; extra keys are ignored.
`**rest` captures the remaining items as a dict. Keys must be literals or dotted names.

```python
def handle(event):
    match event:
        case {"type": "click", "pos": (x, y)}:
            return f"click {x},{y}"
        case {"type": "error", **details}:
            return f"error {details}"

handle({"type": "error", "code": 500})   # "error {'code': 500}"
```

Gotcha: `case {}` matches *every* mapping (including non-empty ones). To test for an empty
dict, use a guard or `case dict() if not d`.

## 5. Class patterns

`Name(...)` checks `isinstance(value, Name)` and then looks at attributes.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

def where(p):
    match p:
        case Point(x=0, y=0):  return "origin"
        case Point(x=0):       return "on the y axis"
        case Point(x, y):      return f"at {x},{y}"     # positional
        case int() | float():  return "a number"        # type check, no attributes
```

Positional sub-patterns work because `@dataclass` generates `__match_args__ = ("x", "y")`.
Plain classes can define it by hand:

```python
class Vec:
    __match_args__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
```

Built-ins `int()`, `str()`, `float()`, `bool()`, `list()`, `dict()`, ... work as type checks.
`int(x)` captures the value itself. Note `bool` is a subclass of `int`, so test `bool()` first.

## 6. OR patterns, `as`, and guards

```python
match command.split():
    case ["go", ("north" | "south" | "east" | "west") as direction]:
        move(direction)                     # `as` binds the whole sub-pattern
    case ["take", *items] if items:         # guard: extra boolean condition
        take(items)
    case ["quit" | "exit"]:
        stop()
```

- Every alternative in `a | b` must bind the same names.
- A guard (`if ...`) runs only after the pattern matched; if it is false, matching continues
  with the next case.

## 7. Worked example: a tiny expression tree

```python
@dataclass(frozen=True)
class Num: value: float
@dataclass(frozen=True)
class Add: left: object; right: object

def ev(e):
    match e:
        case Num(v):    return v
        case Add(l, r): return ev(l) + ev(r)
        case _:         raise TypeError(f"unknown node {e!r}")

ev(Add(Num(1), Add(Num(2), Num(3))))   # 6
```

Matching on a tuple of values is a handy trick for combining cases:
`match (a, b): case (Num(0), x) | (x, Num(0)): return x`.

## 8. When NOT to use `match`

- **Simple boolean tests**: `if x > 0:` is clearer than a `match` with guards only.
- **Plain value to value mapping**: a `dict` (`{"north": (0, 1)}[d]`) is shorter and faster.
- **Polymorphism you control**: if you own the classes, a method (`shape.area()`) beats
  a central `match` on type. `match` shines when you do not own the data (JSON, ASTs,
  parsed commands, protocol messages).
- **Two or three simple branches** where `if`/`elif` reads fine.
- **Validation you need rich errors for**: a pattern that fails gives you no reason.

## Common mistakes
- **Bare name as a constant**: `case MAX:` captures instead of comparing. Use `Cls.MAX`.
- **Order matters**: put specific cases first. `case [x, *_]` before `case [1, 2]` hides it.
- **Forgetting `bool` is an `int`**: `case int():` also matches `True`.
- **Expecting strings to match sequence patterns** (they never do).
- **`case {}` as "empty dict"**: it matches all mappings.
- **Mismatched bindings in `|`**: `case [x] | [y, _]` is a `SyntaxError`.
- **Missing `__match_args__`**: positional class patterns raise `TypeError` for plain classes.
- **Relying on a fall-through default**: add `case _:` and raise or return explicitly.

## Practice
Open `exercises.py`, implement each (for the class, replace the stub with a plain class
that defines `__match_args__`), then run:

```bash
python check.py 3.07
```
