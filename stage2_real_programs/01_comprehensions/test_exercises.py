import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_squares_of_evens():
    assert ex.squares_of_evens([1, 2, 3, 4, 5, 6]) == [4, 16, 36]
    assert ex.squares_of_evens([1, 3]) == []
    assert ex.squares_of_evens([]) == []
    assert ex.squares_of_evens([-2, 0]) == [4, 0]


def test_word_lengths():
    assert ex.word_lengths(["a", "abc", "hello"]) == {"a": 1, "abc": 3, "hello": 5}
    assert ex.word_lengths([]) == {}
    assert ex.word_lengths(["hi", "hi"]) == {"hi": 2}


def test_unique_first_letters():
    assert ex.unique_first_letters(["Apple", "avocado", "Banana", ""]) == {"a", "b"}
    assert ex.unique_first_letters([]) == set()
    assert isinstance(ex.unique_first_letters(["x"]), set)


def test_flatten():
    assert ex.flatten([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]
    assert ex.flatten([]) == []
    assert ex.flatten([[], []]) == []


def test_transpose():
    assert ex.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert ex.transpose([[1, 2]]) == [[1], [2]]
    assert ex.transpose([]) == []
    assert ex.transpose(ex.transpose([[1, 2], [3, 4], [5, 6]])) == [[1, 2], [3, 4], [5, 6]]


def test_invert_dict():
    assert ex.invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert ex.invert_dict({}) == {}


def test_pythagorean_triples():
    assert ex.pythagorean_triples(13) == [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
    assert ex.pythagorean_triples(4) == []
    assert ex.pythagorean_triples(5) == [(3, 4, 5)]
    assert ex.pythagorean_triples(0) == []


def test_count_matching():
    assert ex.count_matching([1, 2, 3, 4], lambda n: n > 2) == 2
    assert ex.count_matching([], lambda n: True) == 0
    assert ex.count_matching("banana", lambda c: c == "a") == 3
    assert ex.count_matching(iter(range(10)), lambda n: n % 2 == 0) == 5  # works on iterators


def test_all_valid_ids():
    assert ex.all_valid_ids(["12", "007"]) is True
    assert ex.all_valid_ids(["12", "x1"]) is False
    assert ex.all_valid_ids([]) is True
    assert ex.all_valid_ids([""]) is False


def test_lazy_squares():
    import types
    g = ex.lazy_squares(4)
    assert isinstance(g, types.GeneratorType)
    assert next(g) == 0
    assert list(g) == [1, 4, 9]
    assert list(ex.lazy_squares(0)) == []
    huge = ex.lazy_squares(10**12)  # would hang/blow memory if it were a list
    assert next(huge) == 0
