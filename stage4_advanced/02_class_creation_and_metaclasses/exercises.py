"""4.02 — Class Creation & Metaclasses

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.02` from the course root to test your work.

Metaclass/descriptor stubs raise NotImplementedError when *used*, so tests
that define classes with them show as "not started" until implemented.
"""
import math
from abc import ABC, abstractmethod


def make_class(name: str, fields, methods=None, bases=()):
    """Build a class dynamically with `type(name, bases, namespace)`.

    - The class is named `name` (`cls.__name__ == name`) and has base classes `bases`.
    - `cls._fields` is a tuple of the field names.
    - `__init__(self, *args)` requires EXACTLY len(fields) positional args
      (otherwise TypeError) and sets each as an instance attribute.
    - `__repr__` returns e.g. `Point(x=1, y=2)` (fields in order, values via repr).
    - `methods` is an optional dict of name -> function added to the class
      namespace; entries in `methods` override the generated ones.

    >>> Point = make_class("Point", ["x", "y"], {"norm1": lambda self: abs(self.x) + abs(self.y)})
    >>> p = Point(3, -4); p
    Point(x=3, y=-4)
    >>> p.norm1()
    7
    """
    raise NotImplementedError


def auto_repr(cls):
    """Class decorator that installs a `__repr__` on `cls` and returns `cls`.

    The repr is `ClassName(a=1, b='x')`: the *public* instance attributes
    (names not starting with "_") in `vars(self)` insertion order, values via
    repr. With no public attributes it is `ClassName()`.
    It replaces any __repr__ the class already defines.

    >>> @auto_repr
    ... class P:
    ...     def __init__(self): self.a = 1; self._hidden = 2; self.b = 'x'
    >>> P()
    P(a=1, b='x')
    """
    raise NotImplementedError


class Shape(ABC):
    """Abstract shape. `area` and `perimeter` are abstract (already declared).

    Implement the concrete method `describe()` which returns
    f"{ClassName}: area={area:.2f}, perimeter={perimeter:.2f}"
    e.g. "Rectangle: area=12.00, perimeter=14.00".
    """

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        raise NotImplementedError


class Rectangle(Shape):
    """Rectangle(width, height): concrete Shape. Store `width`, `height`."""

    def __init__(self, width: float, height: float):
        raise NotImplementedError

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError


class Circle(Shape):
    """Circle(radius): concrete Shape using math.pi. Store `radius`."""

    def __init__(self, radius: float):
        raise NotImplementedError

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError


class PluginBase:
    """Plugin registry built on `__init_subclass__`.

    - A class that inherits DIRECTLY from PluginBase is a *root*: it gets its
      own fresh, empty dict as `cls.registry` and is not itself registered.
    - Any deeper subclass (a subclass of a root, or of a plugin) registers
      itself in the inherited `registry` under `key`, given as a class keyword
      argument (`class Csv(Root, key="csv")`), or by default `cls.__name__.lower()`.
    - Registering a key that already exists raises ValueError (class creation fails).
    - Unrelated roots have independent registries.
    - `Root.create(key, *args, **kwargs)` instantiates the registered class;
      an unknown key raises KeyError.
    - Remember to call `super().__init_subclass__()`.

    >>> class Loader(PluginBase): pass
    >>> class Csv(Loader, key="csv"): pass
    >>> class Json(Loader): pass
    >>> sorted(Loader.registry)
    ['csv', 'json']
    """

    def __init_subclass__(cls, key=None, **kwargs):
        raise NotImplementedError

    @classmethod
    def create(cls, key, *args, **kwargs):
        raise NotImplementedError


class SingletonMeta(type):
    """Metaclass making each class that uses it a singleton.

        class Config(metaclass=SingletonMeta): ...
        Config() is Config()        # True

    - The first call creates the instance (arguments are passed to __init__);
      later calls return that same instance WITHOUT calling __init__ again
      (arguments are ignored).
    - Each class has its own instance: a subclass of a singleton class has a
      separate singleton.
    Implement `__call__`.
    """

    def __call__(cls, *args, **kwargs):
        raise NotImplementedError


class EnforcedMeta(type):
    """Metaclass enforcing an interface at class-creation time.

    A class whose own body defines `required_methods` (a tuple of names) is an
    *interface* and is not checked. Every other class created with this
    metaclass must provide, via normal attribute lookup (inheritance counts),
    a CALLABLE attribute for each name in its (inherited) `required_methods`.
    If any are missing raise TypeError at class creation with the message
    f"{name} must implement: a, b" (missing names sorted, joined by ", ").

        class Closeable(metaclass=EnforcedMeta):
            required_methods = ("close", "flush")
        class File(Closeable):
            def close(self): ...      # TypeError: File must implement: flush

    Classes with no `required_methods` anywhere are never rejected.
    Hint: override __new__, call super().__new__ first, then inspect the class.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        raise NotImplementedError


class NoDupMeta(type):
    """Metaclass that forbids defining the same name twice in a class body.

        class Bad(metaclass=NoDupMeta):
            def f(self): ...
            def f(self): ...     # TypeError at class creation

    - Implement `__prepare__` (a classmethod) returning a dict subclass whose
      `__setitem__` raises TypeError (message contains the repr of the name,
      e.g. "duplicate definition of 'f'") when the key already exists.
    - Ordinary classes with distinct names must still be created normally,
      including with base classes and class keyword arguments being ignored.
    """

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        raise NotImplementedError
