# 2.04 — Dunder Methods & Properties

## Learning goals
- Make your own classes behave like built-in types with "dunder" (double underscore) methods
- Write correct `__repr__`, `__str__`, `__eq__`, `__hash__` and ordering methods
- Build container classes (`__len__`, `__getitem__`, `__iter__`, `__contains__`)
- Use `@property`, `@classmethod` and `@staticmethod`

## 1. What are dunder methods?

Python's syntax is translated into method calls. You almost never call dunders directly; you
implement them and the language calls them for you.

| You write | Python calls |
|---|---|
| `repr(x)` / REPL echo | `x.__repr__()` |
| `str(x)` / `print(x)` | `x.__str__()` |
| `a == b` | `a.__eq__(b)` |
| `hash(x)`, `x in set`  | `x.__hash__()` |
| `a < b` | `a.__lt__(b)` |
| `a + b` | `a.__add__(b)` (then `b.__radd__(a)`) |
| `len(x)` | `x.__len__()` |
| `x[i]` | `x.__getitem__(i)` |
| `for i in x` | `x.__iter__()` |
| `i in x` | `x.__contains__(i)` |
| `bool(x)`, `if x:` | `x.__bool__()` (else `__len__`) |
| `abs(x)`, `-x` | `__abs__`, `__neg__` |

## 2. `__repr__` and `__str__`

`__repr__` is for **developers**: unambiguous, ideally valid Python that recreates the object.
`__str__` is for **users**. If only `__repr__` exists, `str()` falls back to it — so always write
`__repr__` first.

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"      # !r applies repr() to the values
    def __str__(self):
        return f"({self.x}, {self.y})"
```

## 3. Equality and hashing

By default `==` compares identity. Define `__eq__` to compare by value. Return
`NotImplemented` (not `False`) for types you don't understand, letting Python try the other side:

```python
def __eq__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented
    return (self.x, self.y) == (other.x, other.y)

def __hash__(self):
    return hash((self.x, self.y))
```

**The hash contract:** equal objects must have equal hashes. Defining `__eq__` without
`__hash__` makes the class **unhashable** (so no sets/dict keys) — Python does this on purpose.
Only hash by fields that never change; mutable objects should stay unhashable (`__hash__ = None`).

## 4. Ordering

Implement `__lt__` and `__eq__`, then let `functools.total_ordering` derive `<=`, `>`, `>=`:

```python
import functools

@functools.total_ordering
class Version:
    def __init__(self, major, minor): ...
    def __eq__(self, other): ...
    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)
```

Comparing tuples is the easiest way to get lexicographic ordering. With `__lt__` defined,
`sorted()`, `min()` and `max()` work on your objects.

## 5. Operator overloading

```python
def __add__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented
    return Vector(self.x + other.x, self.y + other.y)

def __mul__(self, k):            # v * 2
    return Vector(self.x * k, self.y * k)
__rmul__ = __mul__               # 2 * v  (called when the left operand can't handle it)
```

Return **new** objects from arithmetic; don't mutate `self`. Returning `NotImplemented`
makes `Vector(1, 2) + 5` raise a clean `TypeError`. `sum(items)` starts with `0 + items[0]`,
so supporting `sum` means an `__radd__` that accepts `0`.

## 6. Containers

Implement a few methods and you get the rest of the sequence behaviour:

```python
class Playlist:
    def __init__(self, name, songs=None):
        self.name = name
        self._songs = list(songs or [])     # copy! never keep the caller's list
    def __len__(self):          return len(self._songs)
    def __getitem__(self, i):   return self._songs[i]    # ints AND slices
    def __iter__(self):         return iter(self._songs)
    def __contains__(self, s):  return s in self._songs
```

If you define only `__getitem__`, iteration and `in` still work through the legacy protocol,
but defining `__iter__` is clearer and faster. `__len__` also gives `bool()` for free
(empty means falsy). Generators make `__iter__` easy: `def __iter__(self): yield self.x; yield self.y`.

## 7. Properties

A property looks like an attribute but runs code. Use it to validate, compute, or keep an API
stable when internals change.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius            # goes through the setter below

    @property
    def celsius(self):                    # getter
        return self._celsius

    @celsius.setter
    def celsius(self, value):             # setter with validation
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def kelvin(self):                     # no setter => read-only
        return self._celsius + 273.15
```

Start with plain attributes. Convert to a property only when you need behaviour — callers
don't have to change, which is why Python code rarely uses `get_x()`/`set_x()`.

## 8. `@classmethod` and `@staticmethod`

| Decorator | First parameter | Typical use |
|---|---|---|
| (none) | `self` — the instance | normal behaviour |
| `@classmethod` | `cls` — the class | **alternate constructors**, working with subclasses |
| `@staticmethod` | nothing | utility that belongs with the class but needs neither |

```python
class Version:
    @classmethod
    def parse(cls, text):                 # Version.parse("1.2.3")
        major, minor, patch = map(int, text.split("."))
        return cls(major, minor, patch)   # `cls`, so subclasses build themselves

    @staticmethod
    def is_valid(text):
        return text.count(".") == 2
```

## Common mistakes

| Mistake | Fix |
|---|---|
| `__eq__` without `__hash__`, then using objects in a set | Define both, consistently |
| Hashing mutable fields | Keep hashed objects immutable, or don't hash them |
| `__repr__` that doesn't help debugging (`<Foo object at 0x...>`) | Show the important fields |
| Returning `False` for foreign types in `__eq__` | Return `NotImplemented` |
| Mutating `self` in `__add__` | Build and return a new object |
| `__str__` returning a non-string | Always return `str` |
| Property setter named differently from the getter | `@x.setter def x(...)` — same name |
| Setting `self.celsius` in the setter (infinite recursion) | Store in `self._celsius` |
| `__len__` returning a float or negative number | Must be a non-negative `int` |

## Practice

You will build `Vector`, `Money` (integer cents, never floats for money!), a `Playlist`
container, a `Temperature` with validated properties, and an ordered `Version`.

Experiment in the REPL: what does `print(Vector(1, 2))` show with and without `__str__`?

```
python check.py 2.04
```
