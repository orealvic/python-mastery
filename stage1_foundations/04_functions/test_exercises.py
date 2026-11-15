import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_greet():
    assert ex.greet("Ada") == "Hello, Ada!"
    assert ex.greet("Ada", "Hi") == "Hi, Ada!"
    assert ex.greet("Ada", "Hi", punctuation="?") == "Hi, Ada?"
    assert ex.greet(name="Bob", punctuation=".") == "Hello, Bob."


def test_add_item_fresh_list_each_call():
    assert ex.add_item(1) == [1]
    assert ex.add_item(2) == [2]
    assert ex.add_item(3) == [3]


def test_add_item_mutates_given_list():
    shared = [1]
    result = ex.add_item(2, shared)
    assert result is shared
    assert shared == [1, 2]
    assert ex.add_item(3, items=shared) == [1, 2, 3]


def test_total():
    assert ex.total(1, 2, 3) == 6
    assert ex.total() == 0
    assert ex.total(2.5) == 2.5
    assert ex.total(*[1, 2, 3, 4]) == 10


def test_describe_options():
    assert ex.describe_options(size=3, color="red") == "color=red, size=3"
    assert ex.describe_options() == ""
    assert ex.describe_options(a=1) == "a=1"
    assert ex.describe_options(**{"z": True, "b": None}) == "b=None, z=True"


def test_min_max():
    assert ex.min_max([3, 1, 4, 1, 5]) == (1, 5)
    assert ex.min_max([7]) == (7, 7)
    assert ex.min_max([-2.5, -1]) == (-2.5, -1)
    lo, hi = ex.min_max([2, 9])
    assert (lo, hi) == (2, 9)
    try:
        ex.min_max([])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for empty list")


def test_format_price():
    assert ex.format_price(1234.5) == "$1,234.50"
    assert ex.format_price(0) == "$0.00"
    assert ex.format_price(1234567.891, decimals=0) == "$1,234,568"
    assert ex.format_price(9.99, currency="EUR ", decimals=1) == "EUR 10.0"


def test_format_price_keyword_only():
    assert ex.format_price(5.0, currency="E") == "E5.00"
    try:
        ex.format_price(5.0, "EUR")
    except TypeError:
        pass
    else:
        raise AssertionError("currency must be keyword-only")


def test_make_multiplier():
    triple = ex.make_multiplier(3)
    assert triple(5) == 15
    assert triple(0) == 0
    half = ex.make_multiplier(0.5)
    assert half(9) == 4.5
    assert triple(2) == 6  # earlier closures are unaffected by later ones


def test_make_counter():
    c = ex.make_counter()
    assert [c(), c(), c()] == [1, 2, 3]
    d = ex.make_counter(10)
    assert d() == 11
    assert c() == 4
    assert d() == 12


def test_sort_words():
    assert ex.sort_words(["pear", "fig", "banana", "apple", "kiwi"]) == [
        "fig", "kiwi", "pear", "apple", "banana",
    ]
    assert ex.sort_words([]) == []
    assert ex.sort_words(["b", "a", "c"]) == ["a", "b", "c"]
    data = ["bb", "a"]
    out = ex.sort_words(data)
    assert data == ["bb", "a"]
    assert out == ["a", "bb"]


def test_compose():
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    assert ex.compose(inc, dbl)(5) == 11
    assert ex.compose(dbl, inc)(5) == 12
    assert ex.compose(str, abs)(-3) == "3"
    assert ex.compose()(42) == 42
    assert ex.compose(inc, inc, inc)(0) == 3
