import importlib
import os
import tracemalloc

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class Key:
    """Hashable item that counts how often __eq__ is called."""

    eq_calls = 0

    def __init__(self, v):
        self.v = v

    def __hash__(self):
        return hash(self.v)

    def __eq__(self, other):
        Key.eq_calls += 1
        return self.v == other.v


def test_timer():
    clock = FakeClock()
    t = ex.Timer(clock=clock)
    assert t.elapsed is None
    with t as same:
        clock.advance(2.5)
    assert same is t
    assert t.elapsed == 2.5
    with t:
        clock.advance(1.0)
    assert t.elapsed == 1.0
    # default clock is a real one: just check it produces a sane number
    with ex.Timer() as real:
        sum(range(1000))
    assert real.elapsed >= 0


def test_timer_records_on_exception():
    clock = FakeClock()
    t = ex.Timer(clock=clock)
    try:
        with t:
            clock.advance(4.0)
            raise KeyError("boom")
    except KeyError:
        pass
    else:
        raise AssertionError("exception must propagate")
    assert t.elapsed == 4.0


def test_best_of():
    clock = FakeClock()
    costs = iter([4, 4, 2, 2, 6, 6])
    calls = []

    def func():
        calls.append(1)
        clock.advance(next(costs))

    assert ex.best_of(func, repeat=3, number=2, clock=clock) == 2.0
    assert len(calls) == 6

    clock2 = FakeClock()
    assert ex.best_of(lambda: clock2.advance(0.5), repeat=4, number=5, clock=clock2) == 0.5


def _leaf():
    return sum(range(100))


def _helper():
    return [_leaf() for _ in range(5)]


def _outer():
    _helper()
    return _leaf()


def test_top_functions_calls():
    names = ex.top_functions(_outer, n=10, sort="calls")
    assert all(isinstance(n, str) for n in names)
    assert names[0] == "_leaf"          # called 6 times, the others once
    assert {"_outer", "_helper", "_leaf"} <= set(names)
    assert not any(n.startswith("{") for n in names)   # no built-ins


def test_top_functions_cumulative_and_limit():
    names = ex.top_functions(_outer, n=10)
    assert names[0] == "_outer"          # the root includes everything else
    assert {"_helper", "_leaf"} <= set(names)
    assert ex.top_functions(_outer, n=1) == ["_outer"]
    assert len(ex.top_functions(_outer, n=2)) == 2
    assert len(ex.top_functions(_outer, n=50)) <= 50


def test_peak_memory():
    size = 1_000_000
    peak = ex.peak_memory(lambda: bytearray(size))
    assert isinstance(peak, int)
    assert size <= peak < 2 * size
    assert not tracemalloc.is_tracing()

    small = ex.peak_memory(lambda: [0] * 100)
    big = ex.peak_memory(lambda: [0] * 100_000)
    assert 0 < small < big

    # a list comprehension materialises everything; a generator does not
    as_list = ex.peak_memory(lambda: sum([i for i in range(200_000)]))
    as_gen = ex.peak_memory(lambda: sum(i for i in range(200_000)))
    assert as_gen < as_list


def test_peak_memory_stops_tracing_on_error():
    def bad():
        bytearray(1000)
        raise ValueError("x")

    try:
        ex.peak_memory(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("exception must propagate")
    assert not tracemalloc.is_tracing()


def test_memoize_lru_unbounded():
    calls = []

    @ex.memoize_lru()
    def add(a, b):
        calls.append((a, b))
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert add(2, 1) == 3
    assert calls == [(1, 2), (2, 1)]
    assert add.cache_info() == {"hits": 1, "misses": 2, "size": 2}
    add.cache_clear()
    assert add.cache_info() == {"hits": 0, "misses": 0, "size": 0}
    add(1, 2)
    assert len(calls) == 3


def test_memoize_lru_eviction():
    calls = []

    @ex.memoize_lru(maxsize=2)
    def sq(x):
        calls.append(x)
        return x * x

    assert (sq(1), sq(2), sq(1), sq(3)) == (1, 4, 1, 9)
    assert calls == [1, 2, 3]
    assert sq.cache_info() == {"hits": 1, "misses": 3, "size": 2}
    sq(1)                       # still cached (2 was evicted)
    assert calls == [1, 2, 3]
    sq(2)                       # was evicted: recomputed, evicts 3
    assert calls == [1, 2, 3, 2]
    sq(3)
    assert calls == [1, 2, 3, 2, 3]


def test_memoize_lru_errors_not_cached():
    calls = []

    @ex.memoize_lru(maxsize=4)
    def f(x):
        calls.append(x)
        if x < 0:
            raise ValueError("neg")
        return x

    for _ in range(2):
        try:
            f(-1)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
    assert calls == [-1, -1]
    assert f.cache_info()["size"] == 0


def test_memoize_lru_fib_is_linear():
    calls = []

    @ex.memoize_lru()
    def fib(n):
        calls.append(n)
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(60) == 1548008755920
    assert len(calls) == 61


def test_common_elements_correctness():
    assert ex.common_elements([3, 1, 3, 2, 5], [5, 3, 9]) == [3, 5]
    assert ex.common_elements([], [1]) == []
    assert ex.common_elements([1, 2], []) == []
    assert ex.common_elements("hello", "world") == ["l", "o"]
    assert ex.common_elements(iter([2, 2, 1]), iter([1, 2])) == [2, 1]


def test_common_elements_counts_operations():
    Key.eq_calls = 0
    a = [Key(i) for i in range(3000)]
    b = [Key(i) for i in range(1500, 4500)]
    result = ex.common_elements(a, b)
    assert [k.v for k in result] == list(range(1500, 3000))
    assert all(r is a[r.v] for r in result)      # the original objects
    # a list scan would need millions of comparisons; hashing needs ~one per match
    assert Key.eq_calls < 20_000, Key.eq_calls


def test_top_k():
    assert ex.top_k([5, 1, 9, 3, 7], 3) == [9, 7, 5]
    assert ex.top_k(["bb", "a", "dddd", "ccc"], 2, key=len) == ["dddd", "ccc"]
    assert ex.top_k(iter(range(1000)), 3) == [999, 998, 997]
    assert ex.top_k((x % 7 for x in range(100)), 2) == [6, 6]
    assert ex.top_k([1, 2], 0) == []
    assert ex.top_k([1, 2], -3) == []
    assert ex.top_k([2, 3, 1], 10) == [3, 2, 1]
    assert ex.top_k([], 3) == []


def test_top_k_uses_heap_not_full_sort():
    class Counted:
        compares = 0

        def __init__(self, v):
            self.v = v

        def __lt__(self, other):
            Counted.compares += 1
            return self.v < other.v

    n = 20_000
    items = [Counted((i * 7919) % n) for i in range(n)]
    result = ex.top_k(items, 5)
    assert [c.v for c in result] == [n - 1, n - 2, n - 3, n - 4, n - 5]
    # a full sort needs ~ n*log2(n) = 285_000 comparisons; a size-5 heap far fewer
    assert Counted.compares < 100_000, Counted.compares


def test_nearest():
    vals = [1, 4, 9, 16]
    assert ex.nearest(vals, 6) == 4
    assert ex.nearest(vals, 6.6) == 9
    assert ex.nearest(vals, 0) == 1
    assert ex.nearest(vals, 100) == 16
    assert ex.nearest(vals, 9) == 9
    assert ex.nearest([1, 5], 3) == 1            # tie -> smaller
    assert ex.nearest([7], -3) == 7
    assert ex.nearest(list(range(0, 1_000_000, 10)), 123_456) == 123_460
    try:
        ex.nearest([], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_nearest_uses_log_lookups():
    class Seq(list):
        reads = 0

        def __getitem__(self, i):
            Seq.reads += 1
            return super().__getitem__(i)

    seq = Seq(range(0, 100_000, 2))
    assert ex.nearest(seq, 12_345) == 12_344
    assert Seq.reads < 100, Seq.reads


def test_slotted_point():
    p = ex.SlottedPoint(1, 2)
    assert (p.x, p.y) == (1, 2)
    assert not hasattr(p, "__dict__")
    assert "x" in ex.SlottedPoint.__slots__ or "x" in ex.SlottedPoint.__dict__
    p.x = 10
    assert p.x == 10
    try:
        p.z = 3
    except AttributeError:
        pass
    else:
        raise AssertionError("expected AttributeError")
    assert repr(ex.SlottedPoint(1, 2)) == "SlottedPoint(x=1, y=2)"
    assert ex.SlottedPoint(1, 2) == ex.SlottedPoint(1, 2)
    assert ex.SlottedPoint(1, 2) != ex.SlottedPoint(2, 1)
    assert ex.SlottedPoint(1, 2) != (1, 2)
    try:
        hash(ex.SlottedPoint(1, 2))
    except TypeError:
        pass
    else:
        raise AssertionError("mutable points must be unhashable")


def test_slotted_point_is_smaller_than_dict_instance():
    import sys

    class Plain:
        def __init__(self, x, y):
            self.x, self.y = x, y

    p = Plain(1, 2)
    assert sys.getsizeof(ex.SlottedPoint(1, 2)) < sys.getsizeof(p) + sys.getsizeof(p.__dict__)


def test_moving_average():
    assert list(ex.moving_average([1, 2, 3, 4, 5], 3)) == [2.0, 3.0, 4.0]
    assert list(ex.moving_average([4, 8], 1)) == [4.0, 8.0]
    assert list(ex.moving_average([1, 2], 3)) == []
    assert list(ex.moving_average([], 2)) == []
    assert list(ex.moving_average(iter([2, 4, 6, 8]), 2)) == [3.0, 5.0, 7.0]
    try:
        list(ex.moving_average([1, 2, 3], 0))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_moving_average_is_lazy():
    consumed = []

    def source():
        for i in range(1, 1_000_000):
            consumed.append(i)
            yield i

    gen = ex.moving_average(source(), 3)
    assert consumed == []                # nothing read before the first request
    assert next(gen) == 2.0
    assert len(consumed) == 3
    assert next(gen) == 3.0
    assert len(consumed) == 4
    assert [next(gen) for _ in range(3)] == [4.0, 5.0, 6.0]
    assert len(consumed) == 7
