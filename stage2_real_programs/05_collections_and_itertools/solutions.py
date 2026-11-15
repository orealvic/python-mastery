"""Reference solutions for 2.05. Try the exercises yourself first!"""
from __future__ import annotations

import itertools
import re
from collections import Counter, OrderedDict, defaultdict, deque, namedtuple
from functools import reduce
from typing import Iterable

Point = namedtuple("Point", ["x", "y"])
"""A 2D point with integer coordinates (provided for you; do not change)."""


def word_frequencies(text: str, n: int) -> list[tuple[str, int]]:
    """Return the `n` most common words in `text` as (word, count) pairs.

    - A word is a maximal run of ASCII letters (a-z, case-insensitive);
      everything else is a separator. Words are lowercased.
    - Sort by count descending; ties keep first-appearance order.
    - If there are fewer than `n` distinct words return them all.
    Hint: `collections.Counter`.

    >>> word_frequencies("The cat and the hat. The END", 2)
    [('the', 3), ('cat', 1)]
    """
    return Counter(re.findall(r"[a-z]+", text.lower())).most_common(n)


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Group words that are anagrams of each other (same letters, same case).

    Groups appear in order of the first member's first appearance; inside a
    group the original order is kept. Hint: `defaultdict(list)` keyed by
    `sorted(word)`.

    >>> group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
    """
    groups: defaultdict[tuple[str, ...], list[str]] = defaultdict(list)
    for word in words:
        groups[tuple(sorted(word))].append(word)
    return list(groups.values())


def farthest_from_origin(text: str) -> Point:
    """Parse points from `"x,y;x,y;..."` (ints) and return the one farthest from (0, 0).

    Return a `Point` (the namedtuple defined above). Distance is compared by
    x*x + y*y; on a tie the first such point wins. Spaces around numbers are
    allowed. Empty (or whitespace-only) text raises ValueError.

    >>> farthest_from_origin("1,2; 3,-4; 0,0")
    Point(x=3, y=-4)
    """
    if not text.strip():
        raise ValueError("no points")
    points = []
    for chunk in text.split(";"):
        x, y = chunk.split(",")
        points.append(Point(int(x), int(y)))
    return max(points, key=lambda p: p.x**2 + p.y**2)


def moving_average(values: list[float], window: int) -> list[float]:
    """Return the average of every full window of `window` consecutive values.

    - `window < 1` raises ValueError.
    - If there are fewer than `window` values, return [].
    - Hint: a `deque(maxlen=window)` slides for you.

    >>> moving_average([1, 2, 3, 4, 5], 3)
    [2.0, 3.0, 4.0]
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    buf: deque[float] = deque(maxlen=window)
    out = []
    for v in values:
        buf.append(v)
        if len(buf) == window:
            out.append(sum(buf) / window)
    return out


def chunked(items: Iterable, n: int) -> list[tuple]:
    """Split `items` into tuples of length `n`; the last one may be shorter.

    `n < 1` raises ValueError. Hint: `itertools.batched` (Python 3.12+).

    >>> chunked("abcdefg", 3)
    [('a', 'b', 'c'), ('d', 'e', 'f'), ('g',)]
    """
    return list(itertools.batched(items, n))


def running_totals(nums: Iterable[int]) -> list[int]:
    """Return the cumulative sums. Hint: `itertools.accumulate`.

    >>> running_totals([1, 2, 3, 4])
    [1, 3, 6, 10]
    >>> running_totals([])
    []
    """
    return list(itertools.accumulate(nums))


def run_length_encode(items: Iterable) -> list[tuple[object, int]]:
    """Collapse runs of equal consecutive items into (item, count) pairs.

    Hint: `itertools.groupby`.

    >>> run_length_encode("aaabccdd")
    [('a', 3), ('b', 1), ('c', 2), ('d', 2)]
    """
    return [(key, sum(1 for _ in group)) for key, group in itertools.groupby(items)]


def combos_summing_to(nums: list[int], k: int, target: int) -> list[tuple[int, ...]]:
    """Return all ways to pick `k` elements (by position) of `nums` that sum to `target`.

    Use `itertools.combinations`, so results come in its order (elements keep
    their original relative order, combinations are in lexicographic order of
    positions). Duplicated values at different positions count separately.

    >>> combos_summing_to([1, 2, 3, 4, 5], 2, 6)
    [(1, 5), (2, 4)]
    """
    return [c for c in itertools.combinations(nums, k) if sum(c) == target]


def product_of(nums: Iterable[int]) -> int:
    """Multiply all numbers together using `functools.reduce`. Empty input -> 1.

    >>> product_of([2, 3, 4])
    24
    >>> product_of([])
    1
    """
    return reduce(lambda a, b: a * b, nums, 1)


class LRUCache:
    """A least-recently-used cache built on `collections.OrderedDict`.

    - `LRUCache(capacity)`: capacity < 1 raises ValueError.
    - `get(key, default=None)`: return the value (and mark the key as most
      recently used), or `default` if missing.
    - `put(key, value)`: insert or update the key, mark it most recently used;
      if the cache now exceeds its capacity, evict the LEAST recently used key.
    - `keys()`: list of keys from least to most recently used.
    - `len(cache)` and `key in cache` work; `in` does NOT change the order.

    >>> c = LRUCache(2)
    >>> c.put("a", 1); c.put("b", 2); c.get("a")
    1
    >>> c.put("c", 3)
    >>> c.keys()
    ['a', 'c']
    """

    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._data: OrderedDict = OrderedDict()

    def get(self, key, default=None):
        if key not in self._data:
            return default
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key, value) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def keys(self) -> list:
        return list(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key) -> bool:
        return key in self._data
