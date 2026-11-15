import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_word_frequencies():
    assert ex.word_frequencies("The cat and the hat. The END", 2) == [("the", 3), ("cat", 1)]
    assert ex.word_frequencies("b a b a c", 5) == [("b", 2), ("a", 2), ("c", 1)]
    assert ex.word_frequencies("", 3) == []
    assert ex.word_frequencies("one, two; one-two!one", 1) == [("one", 3)]
    assert ex.word_frequencies("x y z", 0) == []
    assert ex.word_frequencies("Hello HELLO hello", 1) == [("hello", 3)]


def test_group_anagrams():
    assert ex.group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [
        ["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    assert ex.group_anagrams([]) == []
    assert ex.group_anagrams(["a"]) == [["a"]]
    assert ex.group_anagrams(["ab", "Ba", "ba"]) == [["ab", "ba"], ["Ba"]]
    assert ex.group_anagrams(["ab", "ba", "ab"]) == [["ab", "ba", "ab"]]


def test_farthest_from_origin():
    assert ex.farthest_from_origin("1,2; 3,-4; 0,0") == ex.Point(3, -4)
    r = ex.farthest_from_origin("5,5")
    assert isinstance(r, ex.Point) and r.x == 5 and r._fields == ("x", "y")
    assert ex.farthest_from_origin("3,4;-4,3;0,1") == ex.Point(3, 4)  # tie: first wins
    assert ex.farthest_from_origin(" 1 , 1 ;2,2 ") == ex.Point(2, 2)
    assert raises(ValueError, ex.farthest_from_origin, "")
    assert raises(ValueError, ex.farthest_from_origin, "   ")


def test_moving_average():
    assert ex.moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
    assert ex.moving_average([1, 2, 3], 1) == [1.0, 2.0, 3.0]
    assert ex.moving_average([4, 8], 2) == [6.0]
    assert ex.moving_average([1, 2], 3) == []
    assert ex.moving_average([], 2) == []
    assert raises(ValueError, ex.moving_average, [1, 2, 3], 0)


def test_chunked():
    assert ex.chunked("abcdefg", 3) == [("a", "b", "c"), ("d", "e", "f"), ("g",)]
    assert ex.chunked([1, 2, 3, 4], 2) == [(1, 2), (3, 4)]
    assert ex.chunked([], 3) == []
    assert ex.chunked(iter(range(5)), 10) == [(0, 1, 2, 3, 4)]
    assert raises(ValueError, ex.chunked, [1], 0)


def test_running_totals():
    assert ex.running_totals([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert ex.running_totals([]) == []
    assert ex.running_totals([5]) == [5]
    assert ex.running_totals([3, -3, 3]) == [3, 0, 3]


def test_run_length_encode():
    assert ex.run_length_encode("aaabccdd") == [("a", 3), ("b", 1), ("c", 2), ("d", 2)]
    assert ex.run_length_encode([]) == []
    assert ex.run_length_encode([1, 1, 2, 1]) == [(1, 2), (2, 1), (1, 1)]
    assert ex.run_length_encode("x") == [("x", 1)]


def test_combos_summing_to():
    assert ex.combos_summing_to([1, 2, 3, 4, 5], 2, 6) == [(1, 5), (2, 4)]
    assert ex.combos_summing_to([1, 2, 3], 3, 6) == [(1, 2, 3)]
    assert ex.combos_summing_to([1, 2, 3], 2, 100) == []
    assert ex.combos_summing_to([2, 2, 2], 2, 4) == [(2, 2), (2, 2), (2, 2)]
    assert ex.combos_summing_to([], 0, 0) == [()]
    assert ex.combos_summing_to([1, 2, 3], 0, 5) == []


def test_product_of():
    assert ex.product_of([2, 3, 4]) == 24
    assert ex.product_of([]) == 1
    assert ex.product_of([7]) == 7
    assert ex.product_of(range(1, 6)) == 120
    assert ex.product_of([5, 0, 3]) == 0


def test_lru_cache_basics():
    c = ex.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.keys() == ["a", "c"]
    assert c.get("b") is None
    assert c.get("b", "nope") == "nope"
    assert len(c) == 2
    assert "a" in c and "b" not in c


def test_lru_cache_ordering():
    c = ex.LRUCache(3)
    for k in "abc":
        c.put(k, k.upper())
    assert c.keys() == ["a", "b", "c"]
    assert "a" in c  # `in` must not refresh
    assert c.keys() == ["a", "b", "c"]
    c.put("a", "A2")  # update refreshes
    assert c.keys() == ["b", "c", "a"]
    assert c.get("a") == "A2"
    c.put("d", "D")  # evicts b
    assert c.keys() == ["c", "a", "d"]
    assert len(c) == 3
    c.get("c")
    assert c.keys() == ["a", "d", "c"]


def test_lru_cache_capacity():
    assert raises(ValueError, ex.LRUCache, 0)
    c = ex.LRUCache(1)
    c.put("x", 1)
    c.put("y", 2)
    assert c.keys() == ["y"] and c.get("x") is None
    c.put("y", 3)
    assert len(c) == 1 and c.get("y") == 3
