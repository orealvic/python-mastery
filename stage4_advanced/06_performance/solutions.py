"""Reference solutions for 4.06. Try the exercises yourself first!"""
import bisect
import cProfile
import heapq
import pstats
import time
import tracemalloc
from collections import OrderedDict, deque


class Timer:
    def __init__(self, clock=time.perf_counter):
        self._clock = clock
        self._start = None
        self.elapsed = None

    def __enter__(self):
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = self._clock() - self._start
        return False


def best_of(func, repeat: int = 5, number: int = 10, clock=time.perf_counter) -> float:
    rounds = []
    for _ in range(repeat):
        start = clock()
        for _ in range(number):
            func()
        rounds.append(clock() - start)
    return min(rounds) / number


def top_functions(func, n: int = 5, sort: str = "cumulative") -> list:
    profiler = cProfile.Profile()
    profiler.runcall(func)
    stats = pstats.Stats(profiler).sort_stats(sort)
    names = [name for (filename, _line, name) in stats.fcn_list if filename != "~"]
    return names[:max(n, 0)]


def peak_memory(func) -> int:
    tracemalloc.start()
    try:
        func()
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak


def memoize_lru(maxsize=None):
    def decorator(func):
        cache = OrderedDict()
        stats = {"hits": 0, "misses": 0}

        def wrapper(*args):
            if args in cache:
                stats["hits"] += 1
                cache.move_to_end(args)
                return cache[args]
            stats["misses"] += 1
            result = func(*args)
            cache[args] = result
            if maxsize is not None and len(cache) > maxsize:
                cache.popitem(last=False)
            return result

        def cache_info():
            return {"hits": stats["hits"], "misses": stats["misses"], "size": len(cache)}

        def cache_clear():
            cache.clear()
            stats["hits"] = stats["misses"] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.__name__ = getattr(func, "__name__", "wrapper")
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def common_elements(a, b) -> list:
    in_b = set(b)
    seen = set()
    result = []
    for x in a:
        if x in in_b and x not in seen:
            seen.add(x)
            result.append(x)
    return result


def top_k(iterable, k: int, key=None) -> list:
    if k <= 0:
        return []
    return heapq.nlargest(k, iterable, key=key)


def nearest(sorted_values: list, x):
    if not sorted_values:
        raise ValueError("empty sequence")
    i = bisect.bisect_left(sorted_values, x)
    if i == 0:
        return sorted_values[0]
    if i == len(sorted_values):
        return sorted_values[-1]
    before, after = sorted_values[i - 1], sorted_values[i]
    return before if x - before <= after - x else after


class SlottedPoint:
    __slots__ = ("x", "y")
    __hash__ = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"SlottedPoint(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, SlottedPoint):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)


def moving_average(iterable, window: int):
    if window < 1:
        raise ValueError("window must be >= 1")
    buf = deque(maxlen=window)
    total = 0
    for item in iterable:
        if len(buf) == window:
            total -= buf[0]
        buf.append(item)
        total += item
        if len(buf) == window:
            yield total / window
