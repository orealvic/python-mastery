import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_dedupe():
    assert ex.dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert ex.dedupe([]) == []
    assert ex.dedupe(["a", "a", "a"]) == ["a"]
    data = [1, 1, 2]
    out = ex.dedupe(data)
    assert data == [1, 1, 2]
    assert out is not data


def test_word_frequency():
    assert ex.word_frequency("the cat and The hat") == {"the": 2, "cat": 1, "and": 1, "hat": 1}
    assert ex.word_frequency("") == {}
    assert ex.word_frequency("  a   A  b ") == {"a": 2, "b": 1}


def test_invert_dict():
    assert ex.invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert ex.invert_dict({}) == {}
    assert ex.invert_dict({1: "x"}) == {"x": 1}


def test_merge_inventories():
    a = {"apple": 3, "pear": 1}
    b = {"apple": 2, "fig": 4}
    assert ex.merge_inventories(a, b) == {"apple": 5, "pear": 1, "fig": 4}
    assert a == {"apple": 3, "pear": 1}
    assert b == {"apple": 2, "fig": 4}
    assert ex.merge_inventories({}, {}) == {}
    assert ex.merge_inventories({"x": 1}, {}) == {"x": 1}


def test_common_elements():
    assert ex.common_elements([3, 1, 2, 2, 5], [2, 3, 3, 9]) == [2, 3]
    assert ex.common_elements([1], [2]) == []
    assert ex.common_elements([], [1]) == []
    assert ex.common_elements(["b", "a"], ["a", "b", "c"]) == ["a", "b"]


def test_group_by_first_letter():
    words = ["apple", "Avocado", "banana", "blueberry", "cherry"]
    assert ex.group_by_first_letter(words) == {
        "a": ["apple", "Avocado"],
        "b": ["banana", "blueberry"],
        "c": ["cherry"],
    }
    assert ex.group_by_first_letter([]) == {}
    assert ex.group_by_first_letter(["Zed", "zoo"]) == {"z": ["Zed", "zoo"]}


def test_transpose():
    assert ex.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert ex.transpose([[1, 2, 3]]) == [[1], [2], [3]]
    assert ex.transpose([[1], [2]]) == [[1, 2]]
    assert ex.transpose([]) == []
    m = [[1, 2], [3, 4]]
    t = ex.transpose(m)
    assert m == [[1, 2], [3, 4]]
    assert t == [[1, 3], [2, 4]]


def test_rotate_left():
    assert ex.rotate_left([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2]
    assert ex.rotate_left([1, 2, 3], 0) == [1, 2, 3]
    assert ex.rotate_left([1, 2, 3], 3) == [1, 2, 3]
    assert ex.rotate_left([1, 2, 3], 4) == [2, 3, 1]
    assert ex.rotate_left([], 5) == []
    data = [1, 2, 3]
    out = ex.rotate_left(data, 1)
    assert data == [1, 2, 3] and out is not data


def test_flatten_once():
    assert ex.flatten_once([[1, 2], [3], [], [[4, 5]]]) == [1, 2, 3, [4, 5]]
    assert ex.flatten_once([]) == []
    assert ex.flatten_once([[], []]) == []
    assert ex.flatten_once([["a"], ["b", "c"]]) == ["a", "b", "c"]


def test_top_scorers():
    scores = {"ann": 90, "bob": 95, "cy": 90}
    assert ex.top_scorers(scores, 2) == [("bob", 95), ("ann", 90)]
    assert ex.top_scorers(scores, 3) == [("bob", 95), ("ann", 90), ("cy", 90)]
    assert ex.top_scorers(scores, 10) == [("bob", 95), ("ann", 90), ("cy", 90)]
    assert ex.top_scorers(scores, 0) == []
    assert ex.top_scorers({}, 3) == []
