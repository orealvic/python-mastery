"""Reference solutions for 3.01. Try the exercises yourself first!"""
from collections import deque
from collections.abc import Iterable, Iterator
from itertools import islice


def take(n: int, iterable: Iterable) -> list:
    return list(islice(iterable, n))


class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def chunked(iterable: Iterable, size: int) -> Iterator[list]:
    if size < 1:
        raise ValueError("size must be >= 1")
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def sliding_window(iterable: Iterable, n: int) -> Iterator[tuple]:
    if n < 1:
        raise ValueError("n must be >= 1")
    window: deque = deque(maxlen=n)
    for item in iterable:
        window.append(item)
        if len(window) == n:
            yield tuple(window)


def flatten(nested: Iterable) -> Iterator:
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


def interleave(*iterables: Iterable) -> Iterator:
    iterators = [iter(i) for i in iterables]
    while iterators:
        alive = []
        for it in iterators:
            try:
                yield next(it)
            except StopIteration:
                continue
            alive.append(it)
        iterators = alive


_LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}


def filter_logs(lines: Iterable[str], min_level: str = "INFO",
                contains: str | None = None) -> Iterator[str]:
    threshold = _LEVELS[min_level]
    needle = contains.lower() if contains is not None else None
    for line in lines:
        parts = line.split(None, 3)
        if len(parts) < 4 or parts[2] not in _LEVELS:
            continue
        level, message = parts[2], parts[3].strip()
        if _LEVELS[level] < threshold:
            continue
        if needle is not None and needle not in message.lower():
            continue
        yield f"{level}: {message}"
