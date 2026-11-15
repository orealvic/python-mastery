# 3.04 — Type Hints

## Learning goals
- Annotate variables, functions, and classes with modern (3.10+) syntax
- Write generic functions and classes with PEP 695 syntax (`def f[T]`, `class Box[T]`, `type X = ...`)
- Describe "shapes" with `Protocol`, `TypedDict`, `Literal`, `Callable`, `overload`
- Narrow types with `isinstance`, `TypeGuard`, and `TypeIs`
- Run a static checker (mypy / pyright) and introspect annotations at runtime

## 1. Hints are not enforced

```python
def greet(name: str, times: int = 1) -> str:
    return ("Hello, " + name + "! ") * times

greet(42)      # Python happily runs this (and crashes inside, or not).
```

Annotations are *metadata*. The interpreter stores them in `__annotations__` and otherwise ignores
them. A separate tool — **mypy** or **pyright** — reads your code and reports contradictions
*before* you run it. They also power editor autocompletion, and libraries such as Pydantic,
FastAPI, and `dataclasses` read them at runtime.

## 2. Basic syntax (modern forms)

```python
count: int = 0
names: list[str] = []
ages: dict[str, int] = {}
point: tuple[float, float] = (1.0, 2.0)       # fixed-length tuple
numbers: tuple[int, ...] = (1, 2, 3)          # variable-length tuple
maybe: str | None = None                      # union / optional (no typing.Optional needed)
ident: int | str = 7

def first(xs: list[int]) -> int | None: ...
def log(msg: str) -> None: ...                # returns nothing
```

Prefer abstract parameter types, concrete return types:

| Parameter type | Accepts |
|---|---|
| `Sequence[T]` | list, tuple, str, range |
| `Iterable[T]` | anything you can loop over once |
| `Mapping[K, V]` | dict and read-only mappings |
| `Collection[T]` | sized iterables |

Import them from `collections.abc`. Use `Any` (from `typing`) only as an escape hatch; `object`
means "anything, but I may not use it".

## 3. `Callable`

```python
from collections.abc import Callable

def apply(f: Callable[[int, int], int], a: int, b: int) -> int:
    return f(a, b)

Handler = Callable[[str], None]          # alias
Any_args: Callable[..., int]             # any parameters
```

## 4. Generics with PEP 695 syntax (3.12+)

Type parameters are declared right in the signature — no `TypeVar` boilerplate:

```python
def first[T](items: Sequence[T]) -> T:
    return items[0]

first([1, 2, 3])      # checker infers int
first("abc")          # str

class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item
    def get(self) -> T:
        return self.item

Box(3).get()          # int
b: Box[str] = Box("x")

def biggest[T: (int, float)](a: T, b: T) -> T: ...   # constrained to those types
def longest[S: Sized](a: S, b: S) -> S: ...           # bound: must be Sized
```

Type aliases use the `type` statement (lazily evaluated, so forward references just work):

```python
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None
type Pair[A, B] = tuple[A, B]
```

(Older code uses `T = TypeVar("T")`, `Generic[T]`, and `X: TypeAlias = ...`. You'll see them
everywhere; they mean the same thing.)

At runtime: `Box.__type_params__` is `(T,)`, `Json.__value__` holds the aliased type.

## 5. `Protocol`: structural typing ("static duck typing")

A class satisfies a protocol if it has the right methods — no inheritance required:

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None: ...

def shutdown(r: SupportsClose) -> None:
    r.close()

shutdown(open("x.txt"))        # OK: files have .close()
```

Add `@runtime_checkable` to allow `isinstance(obj, SupportsClose)` — it checks only that the
*attribute names exist*, not their signatures.

## 6. `TypedDict`, `Literal`, `Final`

```python
from typing import Literal, TypedDict, NotRequired, Final

class Movie(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]

m: Movie = {"title": "Alien", "year": 1979}      # a plain dict at runtime!

Mode = Literal["r", "w", "a"]
def open_it(mode: Mode): ...
open_it("x")                  # checker error

MAX: Final = 10               # constant; reassignment is flagged
```

At runtime `Movie.__required_keys__` and `Movie.__optional_keys__` exist, but constructing
a `Movie` does no validation — it's just a `dict`.

## 7. `overload`

When the return type depends on the argument type:

```python
from typing import overload

@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...
def double(x):                     # the real implementation (unannotated or broad)
    return x * 2
```

The `@overload` stubs exist only for the checker; at runtime only the last `def` survives.

## 8. Type narrowing

Checkers refine types inside `if` branches:

```python
def f(x: int | str | None):
    if x is None: ...              # x: None
    elif isinstance(x, int): ...   # x: int
    else: ...                      # x: str
```

For custom checks write a **type guard**. `TypeIs` (3.13+) narrows both branches and is usually what
you want; `TypeGuard` narrows only the positive branch:

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)
```

Other tools: `assert_never(x)` for exhaustiveness checks, `cast(T, x)` to override (no runtime
effect), `Self` for fluent methods, `@override` (3.12) to flag accidental non-overrides.

## 9. Running a checker

```bash
pip install mypy pyright
mypy --strict src/            # strict: no implicit Any, all defs annotated
pyright src/
```

Configure in `pyproject.toml`:

```toml
[tool.mypy]
strict = true
python_version = "3.14"
```

Tips for adoption: start with `mypy` non-strict, annotate public functions first, use
`# type: ignore[code]` sparingly (always with the error code), and keep the checker in CI.
Third-party libraries without hints need stubs (`pip install types-requests`).

## 10. Runtime introspection

```python
import inspect, typing

def f(a: int, b: "list[str]" = None) -> bool: ...

f.__annotations__                  # raw (may contain strings / lazy objects)
typing.get_type_hints(f)           # resolved: {'a': int, 'b': list[str], 'return': bool}
inspect.signature(f)               # parameters + defaults + annotations

typing.get_origin(list[int])       # list
typing.get_args(dict[str, int])    # (str, int)
typing.get_args(Literal["a", "b"]) # ('a', 'b')
```

Python 3.14 evaluates annotations lazily (PEP 649/749): forward references work without quotes,
and `annotationlib.get_annotations()` offers more control. Use `get_type_hints` for the common case.

## Common mistakes
- **Believing hints validate at runtime.** They don't (unless a library like Pydantic does).
- **Mutable default confusion**: `def f(x: list[int] = [])` is still the mutable default bug.
- **Over-using `Any`**, which silently turns the checker off for that value.
- **`list[int]` is invariant**: you can't pass a `list[bool]` where `list[int]` is expected
  (the callee might append an `int`). Use `Sequence[int]` for read-only access.
- **`Optional[X]` means "X or None"**, not "optional parameter". A default value is separate.
- **Using `TypeGuard` when you want `TypeIs`**, and then losing narrowing in the `else` branch.
- **`isinstance` with a non-runtime Protocol** raises `TypeError`; add `@runtime_checkable`.

## Practice
Open `exercises.py`, implement each, then run:

```bash
python check.py 3.04
```
