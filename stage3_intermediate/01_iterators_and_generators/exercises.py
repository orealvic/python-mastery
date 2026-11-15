"""3.01 — Iterators & Generators

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 3.01` from the course root to test your work.

Unless stated otherwise, functions must be LAZY: they must not consume more
of their input than is needed to produce the values requested so far.
"""
from collections.abc import Iterable, Iterator


def take(n: int, iterable: Iterable) -> list:
    """Return a list of the first n items of `iterable` (fewer if it is shorter).

    Must not consume more than n items. Works on infinite iterables.

    >>> take(3, range(100))
    [0, 1, 2]
    >>> take(5, [1, 2])
    [1, 2]
    """
    raise NotImplementedError


class Countdown:
    """An iterator that counts down from `start` to 1, then stops.

    It must be a real iterator: `iter(c) is c`, and `next(c)` works.
    Once exhausted it stays exhausted. `Countdown(0)` yields nothing.

    >>> list(Countdown(3))
    [3, 2, 1]
    >>> c = Countdown(2); next(c), next(c)
    (2, 1)

    Hint: implement __init__, __iter__ (return self) and __next__
    (raise StopIteration when finished).
    """

    def __init__(self, start: int) -> None:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


def fibonacci() -> Iterator[int]:
    """Infinite generator of Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8, ...

    >>> take(7, fibonacci())
    [0, 1, 1, 2, 3, 5, 8]
    """
    raise NotImplementedError


def chunked(iterable: Iterable, size: int) -> Iterator[list]:
    """Yield successive lists of `size` items. The last list may be shorter.
    Raise ValueError (when first iterated or called) if size < 1.
    Works lazily on infinite iterables.

    >>> list(chunked([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    >>> list(chunked("abc", 5))
    [['a', 'b', 'c']]
    >>> list(chunked([], 3))
    []
    """
    raise NotImplementedError


def sliding_window(iterable: Iterable, n: int) -> Iterator[tuple]:
    """Yield overlapping tuples of length n, advancing one item at a time.
    If the input has fewer than n items, yield nothing.
    Raise ValueError if n < 1.

    >>> list(sliding_window([1, 2, 3, 4], 2))
    [(1, 2), (2, 3), (3, 4)]
    >>> list(sliding_window("abcd", 3))
    [('a', 'b', 'c'), ('b', 'c', 'd')]
    >>> list(sliding_window([1], 2))
    []

    Hint: collections.deque(maxlen=n) is perfect here.
    """
    raise NotImplementedError


def flatten(nested: Iterable) -> Iterator:
    """Recursively flatten arbitrarily nested lists and tuples into a flat
    stream of leaf values. Strings (and bytes) are leaves, NOT flattened.
    Other types (ints, dicts, None, ...) are leaves too.

    >>> list(flatten([1, [2, (3, [4])], 5]))
    [1, 2, 3, 4, 5]
    >>> list(flatten(["ab", ["cd"]]))
    ['ab', 'cd']

    Hint: use `yield from` for the recursive call.
    """
    raise NotImplementedError


def interleave(*iterables: Iterable) -> Iterator:
    """Round-robin over the iterables: one item from each in turn. When an
    iterable runs out, skip it and continue with the others.

    >>> list(interleave([1, 2, 3], "ab", [True]))
    [1, 'a', True, 2, 'b', 3]
    >>> list(interleave())
    []
    """
    raise NotImplementedError


def filter_logs(lines: Iterable[str], min_level: str = "INFO",
                contains: str | None = None) -> Iterator[str]:
    """A lazy log-filtering pipeline.

    Each input line looks like:  "<date> <time> <LEVEL> <message...>"
        e.g. "2024-05-01 12:00:01 ERROR disk full"
    Levels, lowest to highest: DEBUG < INFO < WARNING < ERROR.

    Yield, for each line whose level is >= `min_level` AND (if `contains` is
    given) whose message contains `contains` (case-insensitive), the string
    "LEVEL: message". Skip blank lines and malformed lines (fewer than 4
    whitespace-separated fields, or an unknown level) silently.
    The message is everything after the level, with original inner spacing
    preserved, stripped at the ends.

    >>> logs = ["2024-05-01 12:00:01 INFO started",
    ...         "2024-05-01 12:00:02 ERROR Disk full",
    ...         "garbage",
    ...         "2024-05-01 12:00:03 DEBUG noise"]
    >>> list(filter_logs(logs, "WARNING"))
    ['ERROR: Disk full']
    >>> list(filter_logs(logs, "DEBUG", contains="STARTED"))
    ['INFO: started']

    Must be lazy: it may only read from `lines` as results are requested.
    """
    raise NotImplementedError
