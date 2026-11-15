# 3.05 — Dataclasses & Enums

## Learning goals
- Replace boilerplate classes with `@dataclass`
- Choose the right options: `frozen`, `order`, `slots`, `kw_only`, `field(...)`
- Validate and derive values in `__post_init__`
- Use `Enum`, `IntEnum`, `StrEnum`, `Flag`, and `auto()` for named constants
- Know where Pydantic fits in

## 1. The boilerplate problem

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"
    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
```

`@dataclass` writes `__init__`, `__repr__`, and `__eq__` for you from the annotated fields:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float = 0.0

p = Point(1.5)
p                 # Point(x=1.5, y=0.0)
p == Point(1.5)   # True
```

The annotation is required (it defines a *field*); the type itself is not enforced.
Fields without defaults must come before fields with defaults.

## 2. Mutable defaults: `field(default_factory=...)`

```python
from dataclasses import dataclass, field

@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)   # new list per instance
    # members: list[str] = []      # ValueError: mutable default not allowed
```

`field()` options:

| Option | Meaning |
|---|---|
| `default=` / `default_factory=` | default value / callable producing one |
| `init=False` | not an `__init__` parameter (set it yourself, e.g. in `__post_init__`) |
| `repr=False` | hide from `repr` |
| `compare=False` | ignore in `==` and ordering |
| `hash=` | include in hash (defaults to `compare`) |
| `kw_only=True` | this field is keyword-only |
| `metadata={...}` | free-form data for libraries |

## 3. Class-level options

```python
@dataclass(frozen=True, order=True, slots=True, kw_only=True)
class Version:
    major: int
    minor: int = 0
```

| Option | Effect |
|---|---|
| `frozen=True` | immutable: assignment raises `FrozenInstanceError`; also generates `__hash__` (usable as dict key / set member) |
| `order=True` | adds `<, <=, >, >=` comparing fields as a tuple in declaration order |
| `slots=True` | uses `__slots__`: less memory, faster attribute access, no `__dict__`, no typo attributes |
| `kw_only=True` | all `__init__` parameters keyword-only (clearer call sites, frees up default ordering) |
| `eq=False`, `repr=False`, `init=False` | skip generating those methods |
| `unsafe_hash=True` | force `__hash__` on a mutable class (be careful) |

Note: `eq=True` without `frozen` sets `__hash__ = None` (unhashable), because mutable + equal-by-value
objects can't be safely hashed.

## 4. `__post_init__`: validate and derive

Runs right after the generated `__init__`:

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("dimensions must be positive")
        self.area = self.width * self.height
```

For frozen classes, assign through `object.__setattr__(self, "area", ...)`.
`InitVar[T]` declares an init-only pseudo-field passed to `__post_init__` but not stored.

## 5. Helpers

```python
from dataclasses import asdict, astuple, replace, fields, is_dataclass

p = Point(1, 2)
asdict(p)            # {'x': 1, 'y': 2}   (recursive deep conversion)
astuple(p)           # (1, 2)
replace(p, y=9)      # Point(x=1, y=9) — a modified COPY; the idiom for frozen classes
[f.name for f in fields(p)]   # ['x', 'y']
is_dataclass(p)      # True
```

Inheritance works: subclass fields are appended after the base class's.

## 6. Enums: named constants

```python
from enum import Enum, auto

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()        # auto() picks the next value (3)

Color.RED            # <Color.RED: 1>
Color.RED.name       # 'RED'
Color.RED.value      # 1
Color(2)             # <Color.GREEN: 2>   lookup by value
Color["BLUE"]        # lookup by name
list(Color)          # all members, in definition order
Color.RED is Color.RED   # True — members are singletons: compare with `is` or ==
```

Looking up a bad value raises `ValueError`; a bad name raises `KeyError`.
Members are immutable and hashable. Two names for one value create an *alias*.

### Specialised enums

| Class | Members are also... | Use for |
|---|---|---|
| `IntEnum` | `int` (compare/arith with ints) | codes, HTTP statuses, interop with C-like APIs |
| `StrEnum` (3.11) | `str` (`auto()` gives lowercased name) | values serialised as text |
| `Flag` / `IntFlag` | combinable with `\|`, `&`, `~` | permissions, option sets |

```python
from enum import IntEnum, StrEnum, Flag, auto

class Level(IntEnum):
    LOW = 1; HIGH = 3
Level.LOW < Level.HIGH          # True (plain Enum doesn't support ordering)
Level.HIGH == 3                 # True (a gotcha as well as a feature)

class Mode(StrEnum):
    READ = auto()               # 'read'
f"{Mode.READ}"                 # 'read'

class Perm(Flag):
    R = auto(); W = auto(); X = auto()
rw = Perm.R | Perm.W
Perm.W in rw                    # True
rw & Perm.X                     # <Perm: 0>  (falsy)
```

Enums can have methods and properties, and be created functionally:
`Animal = Enum("Animal", "CAT DOG")`.

Use `@enum.unique` to forbid aliases, and `match` statements with enum members (3.07).

## 7. Dataclasses + enums together

```python
class Status(StrEnum):
    TODO = "todo"; DONE = "done"

@dataclass(slots=True)
class Task:
    title: str
    status: Status = Status.TODO
```

## 8. Where Pydantic fits

Dataclasses do **not** validate or coerce types. **Pydantic** (third-party; not used in this course)
gives you dataclass-like models that *do*: `class User(BaseModel): age: int` parses `"42"`
into `42` and raises `ValidationError` for junk, plus JSON (de)serialisation. Rule of thumb:
dataclasses for internal data you control; Pydantic at boundaries (HTTP, config files, user input).
`attrs` is another popular alternative (dataclasses were inspired by it).

## Common mistakes
- **Mutable default** (`= []`): use `default_factory`.
- **Non-default field after a default field** — `TypeError`; reorder or use `kw_only=True`.
- **Expecting type enforcement.** `Point("a", "b")` works fine.
- **`frozen=True` and `__post_init__` assignment** — use `object.__setattr__` for derived values.
- **Mutating objects inside a frozen dataclass** (a frozen list field can still be appended to).
- **`order=True` without thinking about field order** — comparison follows declaration order.
- **Comparing enum members by value across different enums**: `Color.RED == Shape.CIRCLE` is False
  unless both are `IntEnum`.
- **Using `==` on `Flag` for "contains"**: use `in` or `&`.

## Practice
Open `exercises.py`, implement each (for the classes: replace the stub with a proper
`@dataclass`), then run:

```bash
python check.py 3.05
```
