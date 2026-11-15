import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_take():
    assert ex.take(3, range(100)) == [0, 1, 2]
    assert ex.take(5, [1, 2]) == [1, 2]
    assert ex.take(0, [1, 2]) == []
    consumed = []

    def src():
        for i in range(10):
            consumed.append(i)
            yield i

    assert ex.take(3, src()) == [0, 1, 2]
    assert len(consumed) <= 3


def test_countdown():
    assert list(ex.Countdown(3)) == [3, 2, 1]
    assert list(ex.Countdown(0)) == []
    c = ex.Countdown(2)
    assert iter(c) is c
    assert next(c) == 2
    assert next(c) == 1
    try:
        next(c)
        assert False, "expected StopIteration"
    except StopIteration:
        pass
    assert list(c) == []


def test_fibonacci():
    assert ex.take(10, ex.fibonacci()) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    g = ex.fibonacci()
    assert next(g) == 0
    assert next(g) == 1
    assert iter(g) is g


def test_chunked():
    assert list(ex.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(ex.chunked("abc", 5)) == [["a", "b", "c"]]
    assert list(ex.chunked([], 3)) == []
    assert list(ex.chunked(range(6), 3)) == [[0, 1, 2], [3, 4, 5]]
    assert ex.take(2, ex.chunked(ex.fibonacci(), 3)) == [[0, 1, 1], [2, 3, 5]]


def test_chunked_invalid_size():
    try:
        list(ex.chunked([1, 2], 0))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_sliding_window():
    assert list(ex.sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(ex.sliding_window("abcd", 3)) == [("a", "b", "c"), ("b", "c", "d")]
    assert list(ex.sliding_window([1], 2)) == []
    assert list(ex.sliding_window([1, 2], 1)) == [(1,), (2,)]
    assert ex.take(2, ex.sliding_window(ex.fibonacci(), 2)) == [(0, 1), (1, 1)]
    try:
        list(ex.sliding_window([1], 0))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_flatten():
    assert list(ex.flatten([1, [2, (3, [4])], 5])) == [1, 2, 3, 4, 5]
    assert list(ex.flatten(["ab", ["cd"]])) == ["ab", "cd"]
    assert list(ex.flatten([])) == []
    assert list(ex.flatten([[], [[]], None, {"a": 1}])) == [None, {"a": 1}]
    assert list(ex.flatten([b"xy", [1]])) == [b"xy", 1]


def test_interleave():
    assert list(ex.interleave([1, 2, 3], "ab", [True])) == [1, "a", True, 2, "b", 3]
    assert list(ex.interleave()) == []
    assert list(ex.interleave([], [1])) == [1]
    assert ex.take(4, ex.interleave(ex.fibonacci(), "ab")) == [0, "a", 1, "b"]


def test_filter_logs():
    logs = [
        "2024-05-01 12:00:01 INFO started",
        "2024-05-01 12:00:02 ERROR Disk full",
        "garbage",
        "",
        "2024-05-01 12:00:03 DEBUG noise",
        "2024-05-01 12:00:04 WARNING  low   memory  ",
        "2024-05-01 12:00:05 TRACE unknown level",
        "2024-05-01 12:00:06 ERROR",
    ]
    assert list(ex.filter_logs(logs, "WARNING")) == [
        "ERROR: Disk full",
        "WARNING: low   memory",
    ]
    assert list(ex.filter_logs(logs)) == [
        "INFO: started",
        "ERROR: Disk full",
        "WARNING: low   memory",
    ]
    assert list(ex.filter_logs(logs, "DEBUG", contains="STARTED")) == ["INFO: started"]
    assert list(ex.filter_logs(logs, "ERROR", contains="nothing")) == []


def test_filter_logs_is_lazy():
    pulled = []

    def source():
        for i in range(1000):
            pulled.append(i)
            yield f"2024-05-01 12:00:00 ERROR event {i}"

    out = ex.filter_logs(source(), "ERROR")
    assert pulled == []  # nothing read until iterated
    assert next(out) == "ERROR: event 0"
    assert len(pulled) == 1
    assert next(out) == "ERROR: event 1"
    assert len(pulled) == 2
