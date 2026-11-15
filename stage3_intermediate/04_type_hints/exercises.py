"""3.04 — Type Hints

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 3.04` from the course root to test your work.

Static types are checked by mypy/pyright, but here we test behaviour at
RUNTIME -- including introspection of the annotations themselves.
Write proper annotations on everything you implement (the tests check some).
"""
from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict, TypeIs, get_args, get_origin, get_type_hints, overload, runtime_checkable
import types
import typing


# ---- Given (do not change): shapes used by the exercises below ------------

@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


class Movie(TypedDict):
    title: str
    year: int


# ---- Exercises -------------------------------------------------------------

class Stack[T]:
    """A generic LIFO stack declared with PEP 695 syntax (`class Stack[T]`).

    Methods:
        push(item: T) -> None
        pop() -> T            raises IndexError("pop from empty stack") if empty
        peek() -> T           returns top without removing; same IndexError
        __len__() -> int
        is_empty() -> bool
    `Stack()` starts empty. Also support iteration from top to bottom via
    __iter__ (so list(stack) == [top, ..., bottom]) without modifying it.

    >>> s = Stack[int]()
    >>> s.push(1); s.push(2)
    >>> s.pop(), len(s)
    (2, 1)
    """

    def __init__(self) -> None:
        raise NotImplementedError


def first[T](items: Sequence[T], default: T | None = None) -> T | None:
    """Return the first element of `items`, or `default` if it is empty.

    >>> first([3, 4])
    3
    >>> first([], "x")
    'x'
    >>> first("abc")
    'a'
    """
    raise NotImplementedError


def close_all(things: Sequence[object]) -> int:
    """Call .close() on every item that satisfies the SupportsClose protocol
    (use isinstance with the runtime-checkable protocol above). Skip others.
    Return the number of items closed.

    >>> close_all([open_file, 42, "x", another_closeable])  # doctest: +SKIP
    2
    """
    raise NotImplementedError


def conforms_to_movie(data: object) -> TypeIs[Movie]:
    """Runtime check that `data` is a valid Movie: a dict with EXACTLY the
    keys 'title' and 'year', where title is a str and year is an int
    (bool is NOT accepted as an int here). Non-dicts return False.

    Declared as a TypeIs so type checkers narrow `data` to Movie.

    >>> conforms_to_movie({"title": "Alien", "year": 1979})
    True
    >>> conforms_to_movie({"title": "Alien"})
    False
    """
    raise NotImplementedError


def describe_signature(func: Callable) -> dict:
    """Return a dict describing the *resolved* annotations of `func`:

        {"params": {name: type, ...}, "return": type}

    * "params" has an entry for each ANNOTATED parameter, in declaration order.
    * "return" is present only if the return annotation exists; for `-> None`
      its value is `type(None)` (what typing.get_type_hints gives).
    * String annotations ("int") must be resolved to real types.

    >>> def f(a: int, b, c: "list[str]" = None) -> bool: ...
    >>> describe_signature(f)   # doctest: +SKIP
    {'params': {'a': <class 'int'>, 'c': list[str]}, 'return': <class 'bool'>}

    Hint: typing.get_type_hints.
    """
    raise NotImplementedError


def format_hint(tp: object) -> str:
    """Render a type hint as readable text.

      * None or NoneType      -> "None"
      * a plain class         -> its __name__          (int -> "int")
      * a union (X | Y, or typing.Optional[X], typing.Union[...])
                              -> members joined by " | "  ("int | None")
      * a parameterised generic (list[int], dict[str, list[int]], tuple[int, ...])
                              -> origin.__name__ + "[" + ", ".join(args) + "]"
        (the Ellipsis in tuple[int, ...] renders as "...")
      * anything else         -> str(tp)

    >>> format_hint(dict[str, list[int]])
    'dict[str, list[int]]'
    >>> format_hint(int | None)
    'int | None'

    Hint: typing.get_origin / typing.get_args; unions have origin
    typing.Union or types.UnionType depending on Python version -- compare
    against both.
    """
    raise NotImplementedError


def literal_values(tp: object) -> tuple:
    """Given a `Literal[...]` type, return its allowed values as a tuple, in
    order. Nested Literals are flattened by typing already. If `tp` is not a
    Literal type raise TypeError.

    >>> literal_values(Literal["r", "w"])
    ('r', 'w')
    """
    raise NotImplementedError


def double(x):
    """Return x doubled: ints are multiplied by 2, strs are repeated twice,
    lists are repeated twice. Anything else raises TypeError.

    Your task: add `@overload` signatures ABOVE this implementation so type
    checkers know int -> int, str -> str, list[T] -> list[T]. (Overloads
    don't change runtime behaviour; the tests check the behaviour.)
    Hint: put `from typing import overload` stubs before the real def, e.g.
        @overload
        def double(x: int) -> int: ...
    Replace this stub with overloads + implementation.

    >>> double(4), double("ab"), double([1])
    (8, 'abab', [1, 1])
    """
    raise NotImplementedError


def group_by[T, K](items: Sequence[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items by key(item), preserving first-seen key order and the
    original order within each group.

    >>> group_by(["apple", "avocado", "banana"], lambda s: s[0])
    {'a': ['apple', 'avocado'], 'b': ['banana']}
    """
    raise NotImplementedError
