import importlib
import os
import typing
from typing import Literal, Optional

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_stack_basic():
    s = ex.Stack()
    assert len(s) == 0 and s.is_empty()
    s.push(1)
    s.push(2)
    s.push(3)
    assert len(s) == 3 and not s.is_empty()
    assert s.peek() == 3
    assert s.pop() == 3
    assert s.pop() == 2
    assert len(s) == 1


def test_stack_empty_errors():
    s = ex.Stack()
    for op in (s.pop, s.peek):
        try:
            op()
            assert False, "expected IndexError"
        except IndexError as e:
            assert "empty" in str(e)


def test_stack_iteration_and_generic():
    s = ex.Stack[str]()  # subscripting works for PEP 695 classes
    for ch in "abc":
        s.push(ch)
    assert list(s) == ["c", "b", "a"]
    assert len(s) == 3  # iteration does not consume
    assert len(ex.Stack.__type_params__) == 1


def test_first():
    assert ex.first([3, 4]) == 3
    assert ex.first([]) is None
    assert ex.first([], "x") == "x"
    assert ex.first("abc") == "a"
    assert ex.first((9,)) == 9
    assert len(ex.first.__type_params__) == 1


def test_close_all():
    class Res:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    a, b = Res(), Res()
    assert ex.close_all([a, 42, "x", b, None]) == 2
    assert a.closed and b.closed
    assert ex.close_all([]) == 0
    assert ex.close_all([1, 2]) == 0


def test_conforms_to_movie():
    assert ex.conforms_to_movie({"title": "Alien", "year": 1979}) is True
    assert ex.conforms_to_movie({"title": "Alien"}) is False
    assert ex.conforms_to_movie({"title": "Alien", "year": "1979"}) is False
    assert ex.conforms_to_movie({"title": 1, "year": 1979}) is False
    assert ex.conforms_to_movie({"title": "A", "year": 1, "extra": 1}) is False
    assert ex.conforms_to_movie({"title": "A", "year": True}) is False
    assert ex.conforms_to_movie([("title", "A")]) is False
    assert ex.conforms_to_movie(None) is False


def test_describe_signature():
    def f(a: int, b, c: "list[str]" = None) -> bool:
        return True

    assert ex.describe_signature(f) == {
        "params": {"a": int, "c": list[str]},
        "return": bool,
    }
    assert list(ex.describe_signature(f)["params"]) == ["a", "c"]

    def g(x):
        pass

    assert ex.describe_signature(g) == {"params": {}}

    def h(x: str) -> None:
        pass

    assert ex.describe_signature(h) == {"params": {"x": str}, "return": type(None)}


def test_format_hint():
    assert ex.format_hint(int) == "int"
    assert ex.format_hint(None) == "None"
    assert ex.format_hint(type(None)) == "None"
    assert ex.format_hint(list[int]) == "list[int]"
    assert ex.format_hint(dict[str, list[int]]) == "dict[str, list[int]]"
    assert ex.format_hint(int | None) == "int | None"
    assert ex.format_hint(Optional[str]) == "str | None"
    assert ex.format_hint(int | str | None) == "int | str | None"
    assert ex.format_hint(tuple[int, ...]) == "tuple[int, ...]"
    assert ex.format_hint(list[int | None]) == "list[int | None]"


def test_literal_values():
    assert ex.literal_values(Literal["r", "w"]) == ("r", "w")
    assert ex.literal_values(Literal[1, 2, 3]) == (1, 2, 3)
    try:
        ex.literal_values(int)
        assert False, "expected TypeError"
    except TypeError:
        pass


def test_double():
    assert ex.double(4) == 8
    assert ex.double("ab") == "abab"
    assert ex.double([1, 2]) == [1, 2, 1, 2]
    for bad in (None, 1.5, {"a": 1}):
        try:
            ex.double(bad)
            assert False, "expected TypeError"
        except TypeError:
            pass


def test_group_by():
    assert ex.group_by(["apple", "avocado", "banana", "blueberry", "cherry"], lambda s: s[0]) == {
        "a": ["apple", "avocado"],
        "b": ["banana", "blueberry"],
        "c": ["cherry"],
    }
    assert ex.group_by([], len) == {}
    result = ex.group_by([3, 1, 4, 1, 5, 9, 2, 6], lambda n: n % 2)
    assert list(result) == [1, 0]  # first-seen key order
    assert result[1] == [3, 1, 1, 5, 9]
    assert result[0] == [4, 2, 6]
    assert len(ex.group_by.__type_params__) == 2
