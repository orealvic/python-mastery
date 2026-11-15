"""Reference solutions for 2.01. Try the exercises yourself first!"""
from __future__ import annotations

from typing import Callable, Iterable, Iterator


def squares_of_evens(nums: list[int]) -> list[int]:
    """Return the squares of the even numbers in `nums`, in the original order.

    >>> squares_of_evens([1, 2, 3, 4, 5, 6])
    [4, 16, 36]
    >>> squares_of_evens([1, 3])
    []
    """
    return [n * n for n in nums if n % 2 == 0]


def word_lengths(words: list[str]) -> dict[str, int]:
    """Map each word to its length. Use a dict comprehension.

    >>> word_lengths(["a", "abc", "hello"])
    {'a': 1, 'abc': 3, 'hello': 5}
    """
    return {w: len(w) for w in words}


def unique_first_letters(words: list[str]) -> set[str]:
    """Return the set of lowercase first letters of the non-empty words.

    Empty strings are skipped. Use a set comprehension.

    >>> sorted(unique_first_letters(["Apple", "avocado", "Banana", ""]))
    ['a', 'b']
    """
    return {w[0].lower() for w in words if w}


def flatten(matrix: list[list[int]]) -> list[int]:
    """Flatten a list of lists into one list, row by row.

    Hint: a comprehension may have two `for` clauses; the *outer* loop comes first.

    >>> flatten([[1, 2], [3], [], [4, 5]])
    [1, 2, 3, 4, 5]
    """
    return [x for row in matrix for x in row]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a rectangular matrix (rows become columns).

    An empty matrix transposes to an empty list.

    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    """
    if not matrix:
        return []
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


def invert_dict(d: dict[str, int]) -> dict[int, str]:
    """Swap keys and values. Values are guaranteed to be unique and hashable.

    >>> invert_dict({"a": 1, "b": 2})
    {1: 'a', 2: 'b'}
    """
    return {v: k for k, v in d.items()}


def pythagorean_triples(limit: int) -> list[tuple[int, int, int]]:
    """Return all (a, b, c) with 1 <= a < b < c <= limit and a*a + b*b == c*c.

    Return the triples sorted by c, then by a.

    >>> pythagorean_triples(13)
    [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
    """
    return sorted(
        ((a, b, c)
         for c in range(1, limit + 1)
         for a in range(1, c)
         for b in range(a + 1, c)
         if a * a + b * b == c * c),
        key=lambda t: (t[2], t[0]),
    )


def count_matching(items: Iterable, predicate: Callable[[object], bool]) -> int:
    """Count how many items satisfy `predicate`.

    Use `sum()` over a generator expression (no intermediate list).

    >>> count_matching([1, 2, 3, 4], lambda n: n > 2)
    2
    """
    return sum(1 for item in items if predicate(item))


def all_valid_ids(ids: list[str]) -> bool:
    """Return True if every id is a non-empty string of digits only.

    Use `all()` with a generator expression. An empty list is valid (True).

    >>> all_valid_ids(["12", "007"])
    True
    >>> all_valid_ids(["12", "x1"])
    False
    """
    return all(i.isdigit() for i in ids)


def lazy_squares(n: int) -> Iterator[int]:
    """Return a *generator expression* yielding 0, 1, 4, ... (n-1)**2.

    Nothing may be computed until the result is iterated, and the function
    must return a generator (not a list).

    >>> g = lazy_squares(4)
    >>> next(g)
    0
    >>> list(g)
    [1, 4, 9]
    """
    return (i * i for i in range(n))
