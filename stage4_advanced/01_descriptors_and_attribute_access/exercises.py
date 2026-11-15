"""4.01 — Descriptors & Attribute Access

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.01` from the course root to test your work.

Descriptor stubs raise NotImplementedError when *used*, so tests that define
a class with them show as "not started" until you implement them.
"""


def attribute_source(obj, name: str) -> str:
    """Report where `getattr(obj, name)` would find its value, WITHOUT
    calling any descriptor or __getattr__ (use `type(obj).__mro__` and
    `vars()`; do not call getattr/hasattr on obj for `name`).

    Return exactly one of these strings, checking in this order:
      "data descriptor"      - the class (any class in the MRO) defines `name`
                               and the attribute's type has __set__ or __delete__
      "instance"             - `name` is a key in the instance's __dict__
                               (objects without a __dict__ never match this)
      "non-data descriptor"  - the class defines `name` and its type has __get__
      "class"                - the class defines `name` (plain attribute)
      "missing"              - none of the above (even if __getattr__ could supply it)

    Use the FIRST class in the MRO whose __dict__ contains `name`.

    >>> class A:
    ...     x = 1
    ...     def m(self): ...
    ...     p = property(lambda self: 1)
    >>> a = A(); a.y = 2
    >>> [attribute_source(a, n) for n in ("p", "y", "m", "x", "zzz")]
    ['data descriptor', 'instance', 'non-data descriptor', 'class', 'missing']
    """
    raise NotImplementedError


class Typed:
    """Descriptor enforcing the type of an attribute.

        class Person:
            name = Typed(str)
            age = Typed(int)

    - `Typed(expected_type)` takes a type (or tuple of types).
    - `__set_name__` records the attribute name.
    - Assigning a value that is not an instance of `expected_type` raises
      TypeError (message should mention the attribute name).
    - Valid values are stored in `obj.__dict__[name]`.
    - Reading before any assignment raises AttributeError.
    - `Person.name` (access on the class) returns the descriptor itself.
    """

    def __init__(self, expected_type):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError


class Bounded:
    """Numeric descriptor restricted to the inclusive range [low, high].

        class Player:
            health = Bounded(0, 100)

    - Assigning a value outside the range raises ValueError.
    - Assigning a non-number (not int/float) raises TypeError.
    - Reading before assignment raises AttributeError.
    - `Player.health` returns the descriptor itself.
    - Deleting the attribute (`del p.health`) removes the stored value
      (implement `__delete__`); reading afterwards raises AttributeError.
    Different instances must keep independent values.
    """

    def __init__(self, low, high):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError

    def __delete__(self, obj):
        raise NotImplementedError


class cached_property:
    """A re-implementation of functools.cached_property.

        class C:
            @cached_property
            def expensive(self):
                ...

    - The wrapped function runs at most once per instance; the result is
      stored in `obj.__dict__[name]` so later reads never reach the descriptor.
    - It must be a NON-data descriptor (do not define __set__), so assigning
      `obj.expensive = 5` simply works and `del obj.expensive` invalidates.
    - `C.expensive` returns the cached_property object itself.
    - The name comes from `__set_name__`.
    """

    def __init__(self, func):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError


class LoggedAttribute:
    """Descriptor that records every successful read and write in a list.

        log = []
        class Account:
            balance = LoggedAttribute(log)

    - `LoggedAttribute(log)` keeps a reference to the SHARED list `log`.
    - Each successful set appends the tuple ("set", name, value).
    - Each successful get appends ("get", name, value).
    - Reading an unset attribute raises AttributeError and logs nothing.
    - Values are stored per instance in `obj.__dict__[name]`.
    - `Account.balance` returns the descriptor and logs nothing.
    """

    def __init__(self, log: list):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError


class Proxy:
    """Transparent proxy using __getattr__ / __setattr__ / __delattr__.

    - `Proxy(target)` stores the target (bypass your own __setattr__ with
      object.__setattr__ when storing it).
    - Reading an attribute Proxy itself lacks is forwarded to the target
      (`__getattr__`), including methods: `Proxy([1]).append(2)` mutates the list.
    - Setting / deleting any attribute (other than the internal target) is
      forwarded to the target.
    - Unknown attributes raise AttributeError (naturally, via getattr).
    - repr is `Proxy(<repr of target>)`.
    """

    def __init__(self, target):
        raise NotImplementedError

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    def __delattr__(self, name):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class AttrDict(dict):
    """A dict whose keys can also be read/written/deleted as attributes.

    >>> d = AttrDict({"a": 1, "inner": {"b": 2}})
    >>> d.a
    1
    >>> d.inner.b
    2
    >>> d.c = 3; d["c"]
    3
    >>> del d.a; "a" in d
    False

    Rules:
    - Missing key as attribute -> AttributeError (not KeyError).
    - A plain-dict value (exactly `type(v) is dict`) read via attribute is
      converted to an AttrDict AND stored back, so `d.inner is d.inner` and
      `d.inner.b = 5` is visible as `d["inner"]["b"] == 5`.
    - Real dict methods win (`d.keys` is still the method); use d["keys"] for that key.
    - Deleting a missing attribute -> AttributeError.
    """

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    def __delattr__(self, name):
        raise NotImplementedError


class Frozen:
    """Base class for objects that become immutable once constructed.

        class Point(Frozen): pass
        p = Point(x=1, y=2)
        p.x          # 1
        p.x = 5      # AttributeError
        del p.x      # AttributeError
        q = p.replace(x=10)   # new Point(x=10, y=2); p unchanged

    - `__init__(self, **fields)` sets each field as an attribute, THEN freezes.
    - After freezing, __setattr__ and __delattr__ raise AttributeError
      (message mentions the class name).
    - `replace(**changes)` returns a new instance of the same type with
      the changes applied; a key that is not an existing field raises AttributeError.
    - repr: `Point(x=1, y=2)` (class name, fields in insertion order).
    - Hint: keep a private flag in the instance __dict__ and use
      object.__setattr__ to set it; exclude it from repr/replace.
    """

    def __init__(self, **fields):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    def __delattr__(self, name):
        raise NotImplementedError

    def replace(self, **changes):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
