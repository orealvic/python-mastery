"""Reference solutions for 3.04. Try the exercises yourself first!"""
import types
import typing
from collections.abc import Callable, Iterator, Sequence
from typing import Literal, Protocol, TypedDict, TypeIs, get_args, get_origin, get_type_hints, overload, runtime_checkable


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


class Movie(TypedDict):
    title: str
    year: int


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return not self._items

    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)


def first[T](items: Sequence[T], default: T | None = None) -> T | None:
    return items[0] if items else default


def close_all(things: Sequence[object]) -> int:
    closed = 0
    for thing in things:
        if isinstance(thing, SupportsClose):
            thing.close()
            closed += 1
    return closed


def conforms_to_movie(data: object) -> TypeIs[Movie]:
    return (
        isinstance(data, dict)
        and set(data) == {"title", "year"}
        and isinstance(data["title"], str)
        and isinstance(data["year"], int)
        and not isinstance(data["year"], bool)
    )


def describe_signature(func: Callable) -> dict:
    hints = get_type_hints(func)
    result: dict = {"params": {k: v for k, v in hints.items() if k != "return"}}
    if "return" in hints:
        result["return"] = hints["return"]
    return result


def format_hint(tp: object) -> str:
    if tp is None or tp is type(None):
        return "None"
    if tp is Ellipsis:
        return "..."
    origin = get_origin(tp)
    if origin is None:
        return tp.__name__ if isinstance(tp, type) else str(tp)
    args = get_args(tp)
    if origin is typing.Union or origin is types.UnionType:
        return " | ".join(format_hint(a) for a in args)
    if hasattr(origin, "__name__") and args:
        return f"{origin.__name__}[{', '.join(format_hint(a) for a in args)}]"
    return str(tp)


def literal_values(tp: object) -> tuple:
    if get_origin(tp) is not Literal:
        raise TypeError(f"{tp!r} is not a Literal type")
    return get_args(tp)


@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...
@overload
def double[T](x: list[T]) -> list[T]: ...
def double(x):
    if isinstance(x, (int, str, list)) and not isinstance(x, bool):
        return x * 2
    raise TypeError(f"cannot double {type(x).__name__}")


def group_by[T, K](items: Sequence[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    groups: dict[K, list[T]] = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    return groups
