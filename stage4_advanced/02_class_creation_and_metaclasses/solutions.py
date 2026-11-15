"""Reference solutions for 4.02. Try the exercises yourself first!"""
import math
from abc import ABC, abstractmethod


def make_class(name: str, fields, methods=None, bases=()):
    fields = tuple(fields)

    def __init__(self, *args):
        if len(args) != len(fields):
            raise TypeError(f"{name} expects {len(fields)} arguments, got {len(args)}")
        for field, value in zip(fields, args):
            setattr(self, field, value)

    def __repr__(self):
        body = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{type(self).__name__}({body})"

    namespace = {"__init__": __init__, "__repr__": __repr__, "_fields": fields}
    namespace.update(methods or {})
    return type(name, tuple(bases), namespace)


def auto_repr(cls):
    def __repr__(self):
        body = ", ".join(f"{k}={v!r}" for k, v in vars(self).items() if not k.startswith("_"))
        return f"{type(self).__name__}({body})"

    cls.__repr__ = __repr__
    return cls


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width, self.height = width, height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class PluginBase:
    def __init_subclass__(cls, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if PluginBase in cls.__bases__:
            cls.registry = {}
            return
        key = key or cls.__name__.lower()
        if key in cls.registry:
            raise ValueError(f"plugin key {key!r} already registered")
        cls.registry[key] = cls

    @classmethod
    def create(cls, key, *args, **kwargs):
        return cls.registry[key](*args, **kwargs)


class SingletonMeta(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class EnforcedMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        if "required_methods" not in namespace:
            missing = sorted(
                n for n in getattr(cls, "required_methods", ()) if not callable(getattr(cls, n, None))
            )
            if missing:
                raise TypeError(f"{name} must implement: {', '.join(missing)}")
        return cls


class _StrictNamespace(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise TypeError(f"duplicate definition of {key!r}")
        super().__setitem__(key, value)


class NoDupMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return _StrictNamespace()
