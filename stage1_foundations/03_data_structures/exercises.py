"""1.03 — Data Structures

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 1.03` from the course root to test your work.

Unless stated otherwise, functions must NOT modify their arguments.
"""


def dedupe(items: list) -> list:
    """Return a new list with duplicates removed, keeping the first occurrence
    of each item and preserving the original order. Items are hashable.

    >>> dedupe([3, 1, 3, 2, 1])
    [3, 1, 2]
    """
    raise NotImplementedError


def word_frequency(text: str) -> dict[str, int]:
    """Count how often each word appears. Words are separated by whitespace and
    compared case-insensitively (the keys are lowercase). You may assume the
    text contains no punctuation.

    >>> word_frequency("the cat and The hat")
    {'the': 2, 'cat': 1, 'and': 1, 'hat': 1}
    """
    raise NotImplementedError


def invert_dict(d: dict) -> dict:
    """Return a dict with keys and values swapped. You may assume all values
    are unique and hashable.

    >>> invert_dict({"a": 1, "b": 2})
    {1: 'a', 2: 'b'}
    """
    raise NotImplementedError


def merge_inventories(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    """Merge two inventories (item -> quantity) into a NEW dict. Items present
    in both have their quantities added.

    >>> merge_inventories({"apple": 3, "pear": 1}, {"apple": 2, "fig": 4})
    {'apple': 5, 'pear': 1, 'fig': 4}
    """
    raise NotImplementedError


def common_elements(a: list, b: list) -> list:
    """Return a sorted list of the distinct elements that appear in both a and b.
    Elements are hashable and mutually orderable.

    >>> common_elements([3, 1, 2, 2, 5], [2, 3, 3, 9])
    [2, 3]
    """
    raise NotImplementedError


def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    """Group words by their first letter, lowercased. Within each group the
    words keep their original order and original capitalization. You may assume
    no word is empty.

    >>> group_by_first_letter(["apple", "Avocado", "banana", "blueberry", "cherry"])
    {'a': ['apple', 'Avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
    """
    raise NotImplementedError


def transpose(matrix: list[list]) -> list[list]:
    """Transpose a rectangular matrix (rows become columns). Return a new
    list of lists. An empty matrix returns an empty list.

    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    """
    raise NotImplementedError


def rotate_left(items: list, k: int) -> list:
    """Return a NEW list rotated left by k positions. k may be larger than
    len(items) and may be 0; negative k is not tested. An empty list returns
    an empty list.

    >>> rotate_left([1, 2, 3, 4, 5], 2)
    [3, 4, 5, 1, 2]
    """
    raise NotImplementedError


def flatten_once(nested: list[list]) -> list:
    """Flatten a list of lists by exactly one level. Deeper nesting is left alone.

    >>> flatten_once([[1, 2], [3], [], [[4, 5]]])
    [1, 2, 3, [4, 5]]
    """
    raise NotImplementedError


def top_scorers(scores: dict[str, int], n: int) -> list[tuple[str, int]]:
    """Return the n highest-scoring (name, score) tuples, best first.
    Ties are broken alphabetically by name. If n exceeds the number of
    entries, return them all.

    Hint: sorted(..., key=...) with a tuple key like (-score, name).

    >>> top_scorers({"ann": 90, "bob": 95, "cy": 90}, 2)
    [('bob', 95), ('ann', 90)]
    """
    raise NotImplementedError
