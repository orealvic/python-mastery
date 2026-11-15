import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_make_counter():
    c = ex.make_counter()
    assert (c(), c(), c()) == (0, 1, 2)
    d = ex.make_counter(10, 5)
    assert (d(), d()) == (10, 15)
    assert c() == 3  # independent of d
    e = ex.make_counter(step=-1)
    assert (e(), e()) == (0, -1)


def test_memoize():
    calls = []

    @ex.memoize
    def add(a, b):
        """Adds."""
        calls.append((a, b))
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert add(2, 1) == 3
    assert calls == [(1, 2), (2, 1)]
    assert add.cache_info() == {"hits": 1, "misses": 2}
    assert add.__name__ == "add"
    assert add.__doc__ == "Adds."
    add.cache_clear()
    assert add.cache_info() == {"hits": 0, "misses": 0}
    add(1, 2)
    assert len(calls) == 3


def test_memoize_fib_is_fast():
    @ex.memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(80) == 23416728348467685


def test_retry_succeeds_after_failures():
    state = {"n": 0}

    @ex.retry(3, (ValueError,))
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError(f"fail {state['n']}")
        return "ok"

    assert flaky() == "ok"
    assert state["n"] == 3
    assert flaky.__name__ == "flaky"


def test_retry_exhausted_raises_last():
    state = {"n": 0}

    @ex.retry(3, (ValueError,))
    def always():
        state["n"] += 1
        raise ValueError(f"fail {state['n']}")

    try:
        always()
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "fail 3"
    assert state["n"] == 3


def test_retry_other_exceptions_not_retried():
    state = {"n": 0}

    @ex.retry(5, (ValueError,))
    def bad(x, y=0):
        state["n"] += 1
        raise KeyError("nope")

    try:
        bad(1, y=2)
        assert False, "expected KeyError"
    except KeyError:
        pass
    assert state["n"] == 1

    @ex.retry(2)
    def default_catches_all():
        state["n"] += 1
        raise RuntimeError("x")

    try:
        default_catches_all()
    except RuntimeError:
        pass
    assert state["n"] == 3


def test_timer():
    @ex.timer
    def work(x):
        """doc"""
        return x * 2

    assert work.elapsed is None
    assert work.history == []
    assert work(4) == 8
    assert isinstance(work.elapsed, float) and work.elapsed >= 0
    work(1)
    assert len(work.history) == 2
    assert work.history[-1] == work.elapsed
    assert work.__name__ == "work" and work.__doc__ == "doc"


def test_timer_records_on_exception():
    @ex.timer
    def boom():
        raise ValueError("x")

    try:
        boom()
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert len(boom.history) == 1
    assert boom.elapsed is not None


def test_validate_types():
    @ex.validate_types
    def repeat(s: str, n: int = 2, *, sep=""):
        return sep.join([s] * n)

    assert repeat("a", 3) == "aaa"
    assert repeat("a") == "aa"
    assert repeat(s="b", n=2, sep="-") == "b-b"
    for args, kwargs, name in [(("a", "3"), {}, "n"), ((5,), {}, "s"), (("a",), {"n": 2.5}, "n")]:
        try:
            repeat(*args, **kwargs)
            assert False, "expected TypeError"
        except TypeError as e:
            assert name in str(e)
    assert repeat.__name__ == "repeat"


def test_validate_types_skips_unannotated_and_complex():
    @ex.validate_types
    def f(a, b: list[int], c: "str" = "x"):
        return (a, b, c)

    assert f(object(), [1]) is not None
    assert f(1, ["not checked deeply"])[1] == ["not checked deeply"]


def test_limit_calls():
    @ex.limit_calls(2)
    def ping(x=1):
        """Ping."""
        return x

    assert ping() == 1
    assert ping(5) == 5
    assert ping.calls_made == 2
    try:
        ping()
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass
    assert ping.calls_made == 2
    ping.reset()
    assert ping.calls_made == 0
    assert ping(9) == 9
    assert ping.__doc__ == "Ping."


def test_register():
    ex.REGISTRY.clear()

    @ex.register()
    def alpha():
        return "a"

    @ex.register("beta-name")
    def beta():
        return "b"

    assert ex.REGISTRY["alpha"] is alpha
    assert ex.REGISTRY["beta-name"] is beta
    assert alpha() == "a"
    before = dict(ex.REGISTRY)
    try:
        @ex.register("alpha")
        def other():
            pass
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert ex.REGISTRY == before
    ex.REGISTRY.clear()


def test_compose_decorators():
    order = []

    def tag(name):
        def deco(func):
            def wrapper(*a, **k):
                order.append(name)
                return func(*a, **k)
            return wrapper
        return deco

    @ex.compose_decorators(tag("a"), tag("b"), tag("c"))
    def f():
        order.append("f")
        return 1

    assert f() == 1
    assert order == ["a", "b", "c", "f"]

    def g():
        return 2

    assert ex.compose_decorators()(g) is g


def test_count_calls():
    @ex.CountCalls
    def inc(x):
        """Increment."""
        if x < 0:
            raise ValueError
        return x + 1

    assert inc.count == 0
    assert inc(1) == 2
    assert inc(2) == 3
    try:
        inc(-1)
    except ValueError:
        pass
    assert inc.count == 3
    assert inc.__name__ == "inc"
    assert inc.__doc__ == "Increment."
