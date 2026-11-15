"""4.06 — Performance & Profiling

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.06` from the course root to test your work.
"""
import time


class Timer:
    """Context manager that measures elapsed time with an injectable clock.

    - `Timer(clock=time.perf_counter)`: `clock` is a zero-argument callable
      returning the current time as a float.
    - `elapsed` is None before the first use. On leaving the `with` block it is
      set to `clock() - <value of clock() on entering>`. This also happens when
      the block raises; the exception must still propagate.
    - `__enter__` returns the Timer itself. The Timer is reusable: each `with`
      overwrites `elapsed`.

    >>> ticks = iter([10.0, 12.5])
    >>> with Timer(clock=lambda: next(ticks)) as t:
    ...     pass
    >>> t.elapsed
    2.5
    """

    def __init__(self, clock=time.perf_counter):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


def best_of(func, repeat: int = 5, number: int = 10, clock=time.perf_counter) -> float:
    """A tiny `timeit.repeat`: return the best per-call time of `func()`.

    Run `repeat` rounds. Each round calls `func()` (no arguments) `number`
    times and measures the whole round with `clock()` (read once before and once
    after the round). Return `min(round_times) / number`.
    `func` is called exactly `repeat * number` times in total.

    >>> # if the rounds took 8, 4 and 12 "seconds" with number=2:
    >>> # best_of(...) == 4 / 2 == 2.0
    """
    raise NotImplementedError


def top_functions(func, n: int = 5, sort: str = "cumulative") -> list:
    """Profile `func()` (no arguments) with `cProfile` and return the names of
    the top `n` functions as a list of strings, best first.

    - Sort with `pstats`: `sort` is any pstats sort key, e.g. "cumulative",
      "tottime" or "calls".
    - A name is the function name only (`"helper"`, `"<lambda>"`), not the file.
    - Skip built-in/C entries (the ones whose filename is "~"), e.g.
      `{method 'append' of 'list' objects}`: report Python functions only.
    - At most `n` names are returned (fewer if fewer were called).

    >>> def inner(): return sum(range(10))
    >>> def outer(): return [inner() for _ in range(3)]
    >>> top_functions(outer, n=2, sort="calls")[0]
    'inner'
    """
    raise NotImplementedError


def peak_memory(func) -> int:
    """Call `func()` (no arguments) under `tracemalloc` and return the PEAK
    number of bytes allocated while it ran (an int).

    tracemalloc must be stopped again afterwards, even if `func` raises
    (the exception propagates). Assume tracing is not already on when called.

    >>> peak_memory(lambda: bytearray(1_000_000)) >= 1_000_000
    True
    """
    raise NotImplementedError


def memoize_lru(maxsize=None):
    """Decorator factory: a hand-written `functools.lru_cache`.

    - Positional, hashable arguments only.
    - `maxsize=None` means unbounded. Otherwise keep at most `maxsize` results;
      when adding a new one to a full cache, evict the LEAST recently used one.
      A cache hit counts as a "use" (makes that entry the most recent).
    - The wrapper has `cache_info()` returning
      `{"hits": int, "misses": int, "size": int}` and `cache_clear()`, which
      empties the cache and zeroes the counters.
    - A call that raises is not cached (it still counts as a miss).

    >>> @memoize_lru(maxsize=2)
    ... def sq(x): return x * x
    >>> sq(1), sq(2), sq(1), sq(3)      # 3 evicts 2 (1 was used more recently)
    (1, 4, 1, 9)
    >>> sq.cache_info()
    {'hits': 1, 'misses': 3, 'size': 2}
    """
    raise NotImplementedError


def common_elements(a, b) -> list:
    """Return the items of `a` that also occur in `b`, in the order of `a`,
    each at most once (no duplicates in the result). Items are hashable.

    This is the naive version written in O(len(a) * len(b)):

        [x for x in a if x in b_list]       # plus de-duplication

    Rewrite it to run in O(len(a) + len(b)). The tests count how many times
    `__eq__` is called on your items, so a scan of `b` per item will fail.

    >>> common_elements([3, 1, 3, 2, 5], [5, 3, 9])
    [3, 5]
    """
    raise NotImplementedError


def top_k(iterable, k: int, key=None) -> list:
    """Return the `k` largest items of `iterable` (any iterable, maybe a
    one-shot generator), largest first. Use `heapq`; do not sort everything.

    - `key` works as in `sorted` (compare by `key(item)`).
    - `k <= 0` gives `[]`; `k` larger than the input returns all items sorted.

    >>> top_k([5, 1, 9, 3, 7], 3)
    [9, 7, 5]
    >>> top_k(["bb", "a", "dddd", "ccc"], 2, key=len)
    ['dddd', 'ccc']
    """
    raise NotImplementedError


def nearest(sorted_values: list, x):
    """Return the element of the ascending `sorted_values` that is closest to
    `x`, in O(log n) using `bisect`. On a tie return the SMALLER element.
    Raise ValueError if `sorted_values` is empty.

    >>> nearest([1, 4, 9, 16], 6)
    4
    >>> nearest([1, 4, 9, 16], 6.6)
    9
    >>> nearest([1, 5], 3)      # tie -> smaller
    1
    """
    raise NotImplementedError


class SlottedPoint:
    """A 2-D point that uses `__slots__` to save memory.

    - `SlottedPoint(x, y)` stores `x` and `y` (and nothing else).
    - Instances have NO `__dict__`, and assigning any other attribute
      (`p.z = 1`) raises AttributeError.
    - `__repr__` is `SlottedPoint(x=1, y=2)`; two points with equal x and y
      are `==`. (Defining `__eq__` removes the default hash; that is fine,
      but then also set `__hash__ = None` explicitly: points are mutable.)
    """

    def __init__(self, x, y):
        raise NotImplementedError


def moving_average(iterable, window: int):
    """Generator: lazily yield the average (a float) of each full window of
    `window` consecutive items.

    - Consume the input ONE item at a time, only as the caller asks for results
      (the first value needs exactly `window` items read; each next value
      reads exactly one more).
    - Memory use must not grow with the input length (keep only `window`
      items, e.g. in a `collections.deque(maxlen=window)`).
    - Fewer than `window` items yields nothing. `window < 1` raises ValueError
      (raised when the first value is requested is fine).

    >>> list(moving_average([1, 2, 3, 4, 5], 3))
    [2.0, 3.0, 4.0]
    """
    raise NotImplementedError
